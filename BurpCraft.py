from burp import IBurpExtender, IIntruderPayloadGeneratorFactory, IIntruderPayloadGenerator, ITab
from javax.swing import JPanel, JTextArea, JButton, JLabel, JScrollPane, JComboBox, JOptionPane
from java.awt import BorderLayout
from java.awt.event import ActionListener
from java.net import URL, URLEncoder, URLDecoder
from java.nio.charset import StandardCharsets
import base64
import java.io.BufferedReader as BufferedReader
import java.io.InputStreamReader as InputStreamReader
import re
import os


# Define the PayloadHandler class
class PayloadHandler:
    def __init__(self):
        self.encodingStack = []  # Stack to track the sequence of encodings


class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory, ITab, ActionListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName("BurpCraft")
        self.callbacks.registerIntruderPayloadGeneratorFactory(self)

        # Create a PayloadHandler instance to track encoding/decoding sequence
        self.payloadHandler = PayloadHandler()

        # Set up the GUI
        self.panel = JPanel(BorderLayout())
        self.payloadsArea = JTextArea(10, 30)
        self.headingSelector = JComboBox()

        self.fetchPayloadsButton = JButton("Fetch XSS Payload", actionPerformed=self.fetchPayloads)
        self.fetchTraversalPayloadsButton = JButton("Fetch Traversal Payloads", actionPerformed=self.fetchTraversalPayloadsFromGitHub)
        self.saveButton = JButton("Save Custom Payloads", actionPerformed=self.saveCustomPayloads)
        self.loadButton = JButton("Load Custom Payloads", actionPerformed=self.loadCustomPayloads)
        self.clearButton = JButton("Clear Payloads", actionPerformed=self.clearPayloads)
        self.encodeButton = JButton("URL Encode", actionPerformed=self.urlEncodePayloads)
        self.decodeButton = JButton("URL Decode", actionPerformed=self.urlDecodePayloads)
        self.base64EncodeButton = JButton("Base64 Encode", actionPerformed=self.base64EncodePayloads)
        self.base64DecodeButton = JButton("Base64 Decode", actionPerformed=self.base64DecodePayloads)

        # GUI layout
        self.panel.add(JLabel("Your Payloads:"), BorderLayout.NORTH)
        self.panel.add(JScrollPane(self.payloadsArea), BorderLayout.CENTER)

        # Add buttons to the layout
        buttonPanel = JPanel()
        buttonPanel.add(self.headingSelector)
        buttonPanel.add(self.fetchPayloadsButton)
        buttonPanel.add(self.fetchTraversalPayloadsButton)
        buttonPanel.add(self.saveButton)
        buttonPanel.add(self.loadButton)
        buttonPanel.add(self.clearButton)
        buttonPanel.add(self.encodeButton)
        buttonPanel.add(self.decodeButton)
        buttonPanel.add(self.base64EncodeButton)
        buttonPanel.add(self.base64DecodeButton)
        self.panel.add(buttonPanel, BorderLayout.SOUTH)

        # Add panel to Burp UI
        callbacks.addSuiteTab(self)

        # Initialize variables to store payloads and headings
        self.savedPayloadsFile = "custom_payloads.txt"  # File to store payloads
        self.savedPayloads = []
        self.githubPayloads = {}

        # Automatically fetch XSS headings on load
        self.fetchXSSPayloadsFromGitHub()

    def fetchXSSPayloadsFromGitHub(self):
        """Fetch XSS headings from GitHub and populate the dropdown."""
        url = "https://raw.githubusercontent.com/da0x0/XSS_made_easy/refs/heads/main/XSS_Payloads.txt"
        self._fetchHeadingsFromURL(url, "XSS")

    def fetchTraversalPayloadsFromGitHub(self, event=None):
        """Fetch Traversal payloads directly from GitHub and display in payloads area."""
        url = "https://raw.githubusercontent.com/da0x0/XSS_made_easy/refs/heads/main/directory_traversal_payloads.txt"
        try:
            connection = URL(url).openConnection()
            connection.setRequestMethod("GET")
            connection.setConnectTimeout(3000)
            connection.setReadTimeout(3000)

            reader = BufferedReader(InputStreamReader(connection.getInputStream()))
            traversal_payloads = []
            line = reader.readLine()
            while line:
                line = line.strip()
                if line and not line.startswith("%%"):
                    traversal_payloads.append(line)
                line = reader.readLine()
            reader.close()
            connection.disconnect()

            self.payloadsArea.setText("\n".join(traversal_payloads))

        except Exception as e:
            JOptionPane.showMessageDialog(self.panel, "Failed to fetch traversal payloads from GitHub.", "Error", JOptionPane.ERROR_MESSAGE)

    def _fetchHeadingsFromURL(self, url, payload_type):
        """Fetch headings from a specified URL and update dropdown."""
        try:
            connection = URL(url).openConnection()
            connection.setRequestMethod("GET")
            connection.setConnectTimeout(3000)
            connection.setReadTimeout(3000)

            self.githubPayloads.clear()
            self.headingSelector.removeAllItems()
            self.headingSelector.addItem("Select a Payload")

            reader = BufferedReader(InputStreamReader(connection.getInputStream()))
            current_heading = None
            line = reader.readLine()

            while line:
                line = line.strip()
                if line.startswith("%%"):
                    current_heading = line[2:].strip()
                    self.githubPayloads[current_heading] = []
                elif current_heading and line:
                    self.githubPayloads[current_heading].append(line)
                line = reader.readLine()
            reader.close()
            connection.disconnect()

            self.updateHeadingSelector()

        except Exception as e:
            JOptionPane.showMessageDialog(self.panel, "Failed to fetch {} headings from GitHub.".format(payload_type), "Error", JOptionPane.ERROR_MESSAGE)

    def updateHeadingSelector(self):
        self.headingSelector.removeAllItems()
        self.headingSelector.addItem("Select a Payload")
        for heading in self.githubPayloads.keys():
            self.headingSelector.addItem(heading)

    def fetchPayloads(self, event):
        """Fetch and append payloads for multiple selected headings."""
        selected_heading = self.headingSelector.getSelectedItem()
        
        if selected_heading == "Select a Payload":
            JOptionPane.showMessageDialog(self.panel, "Please select a valid payload heading.", "Info", JOptionPane.INFORMATION_MESSAGE)
            return

        if selected_heading in self.githubPayloads:
            current_payloads = self.payloadsArea.getText().strip()
            new_payloads = "\n".join(self.githubPayloads.get(selected_heading, []))
            
            if current_payloads:
                combined_payloads = current_payloads + "\n" + new_payloads
            else:
                combined_payloads = new_payloads

            self.payloadsArea.setText(combined_payloads)
        else:
            JOptionPane.showMessageDialog(self.panel, "No payloads found for the selected heading.", "Error", JOptionPane.ERROR_MESSAGE)

    def saveCustomPayloads(self, event):
        """Save custom payloads to a file."""
        try:
            self.savedPayloads = [payload for payload in self.payloadsArea.getText().splitlines() if payload.strip()]
            with open(self.savedPayloadsFile, "w") as file:
                file.write("\n".join(self.savedPayloads))
            JOptionPane.showMessageDialog(self.panel, "Custom payloads saved successfully.", "Success", JOptionPane.INFORMATION_MESSAGE)
        except Exception as e:
            JOptionPane.showMessageDialog(self.panel, "Error saving custom payloads: {}".format(str(e)), "Error", JOptionPane.ERROR_MESSAGE)

    def loadCustomPayloads(self, event):
        """Load custom payloads from the file."""
        try:
            if os.path.exists(self.savedPayloadsFile):
                with open(self.savedPayloadsFile, "r") as file:
                    self.savedPayloads = [payload for payload in file.read().splitlines() if payload.strip()]
                self.payloadsArea.setText("\n".join(self.savedPayloads))

                # Reset the encoding stack
                self.payloadHandler.encodingStack = []

                # Determine encoding of loaded payloads
                if all(self.is_valid_url_encoded(payload) for payload in self.savedPayloads):
                    self.payloadHandler.encodingStack.append('url_encode')
                elif all(self.is_valid_base64(payload) for payload in self.savedPayloads):
                    self.payloadHandler.encodingStack.append('base64_encode')

                JOptionPane.showMessageDialog(self.panel, "Custom payloads loaded successfully.", "Success", JOptionPane.INFORMATION_MESSAGE)
            else:
                JOptionPane.showMessageDialog(self.panel, "No saved payloads found.", "Info", JOptionPane.INFORMATION_MESSAGE)
        except Exception as e:
            JOptionPane.showMessageDialog(self.panel, "Error loading custom payloads: {}".format(str(e)), "Error", JOptionPane.ERROR_MESSAGE)

    def clearPayloads(self, event):
        """Clear the text area."""
        self.payloadsArea.setText("")
        self.payloadHandler.encodingStack = []  # Reset the encoding stack

    def urlEncodePayloads(self, event):
        """Perform URL encoding on the payloads."""
        try:
            selected_text = self.payloadsArea.getSelectedText()
            lines = self.payloadsArea.getText().splitlines()

            if selected_text:
                start = self.payloadsArea.getSelectionStart()
                end = self.payloadsArea.getSelectionEnd()

                updated_lines = []
                for i, line in enumerate(lines):
                    line_start = self.payloadsArea.getLineStartOffset(i)
                    line_end = self.payloadsArea.getLineEndOffset(i)

                    if line_start <= start < line_end or line_start < end <= line_end:
                        encoded_line = URLEncoder.encode(line, StandardCharsets.UTF_8.toString())
                        updated_lines.append(encoded_line)
                    else:
                        updated_lines.append(line)

                self.payloadsArea.setText("\n".join(updated_lines))
            else:
                encoded_lines = [URLEncoder.encode(line, StandardCharsets.UTF_8.toString()) for line in lines]
                self.payloadsArea.setText("\n".join(encoded_lines))

            self.payloadHandler.encodingStack.append('url_encode')
        except Exception as e:
            JOptionPane.showMessageDialog(self.panel, "Error in URL encoding: {}".format(str(e)), "Error", JOptionPane.ERROR_MESSAGE)


    def urlDecodePayloads(self, event):
        """Perform URL decoding on the payloads."""
        try:
            if not self.payloadHandler.encodingStack or self.payloadHandler.encodingStack[-1] != 'url_encode':
                expected = self.payloadHandler.encodingStack[-1] if self.payloadHandler.encodingStack else "None"
                JOptionPane.showMessageDialog(self.panel, "Decoding not in sequence. Expected encoding: {}".format(expected), "Error", JOptionPane.ERROR_MESSAGE)
                return

            selected_text = self.payloadsArea.getSelectedText()
            lines = self.payloadsArea.getText().splitlines()

            if selected_text:
                start = self.payloadsArea.getSelectionStart()
                end = self.payloadsArea.getSelectionEnd()

                updated_lines = []
                for i, line in enumerate(lines):
                    line_start = self.payloadsArea.getLineStartOffset(i)
                    line_end = self.payloadsArea.getLineEndOffset(i)

                    if line_start <= start < line_end or line_start < end <= line_end:
                        try:
                            decoded_line = URLDecoder.decode(line, StandardCharsets.UTF_8.toString())
                            updated_lines.append(decoded_line)
                        except Exception:
                            updated_lines.append(line)  # Leave unchanged if invalid
                    else:
                        updated_lines.append(line)

                self.payloadsArea.setText("\n".join(updated_lines))
            else:
                decoded_lines = []
                for line in lines:
                    try:
                        decoded_lines.append(URLDecoder.decode(line, StandardCharsets.UTF_8.toString()))
                    except Exception:
                        decoded_lines.append(line)  # Leave unchanged if invalid
                self.payloadsArea.setText("\n".join(decoded_lines))

            self.payloadHandler.encodingStack.pop()
        except Exception as e:
            JOptionPane.showMessageDialog(self.panel, "Error in URL decoding: {}".format(str(e)), "Error", JOptionPane.ERROR_MESSAGE)


    def base64EncodePayloads(self, event):
        """Perform Base64 encoding on the payloads."""
        try:
            selected_text = self.payloadsArea.getSelectedText()
            lines = self.payloadsArea.getText().splitlines()

            if selected_text:
                start = self.payloadsArea.getSelectionStart()
                end = self.payloadsArea.getSelectionEnd()

                updated_lines = []
                for i, line in enumerate(lines):
                    line_start = self.payloadsArea.getLineStartOffset(i)
                    line_end = self.payloadsArea.getLineEndOffset(i)

                    if line_start <= start < line_end or line_start < end <= line_end:
                        encoded_line = base64.b64encode(line.encode("utf-8")).decode("utf-8")
                        updated_lines.append(encoded_line)
                    else:
                        updated_lines.append(line)

                self.payloadsArea.setText("\n".join(updated_lines))
            else:
                encoded_lines = [base64.b64encode(line.encode("utf-8")).decode("utf-8") for line in lines]
                self.payloadsArea.setText("\n".join(encoded_lines))

            self.payloadHandler.encodingStack.append('base64_encode')
        except Exception as e:
            JOptionPane.showMessageDialog(self.panel, "Error in Base64 encoding: {}".format(str(e)), "Error", JOptionPane.ERROR_MESSAGE)


    def base64DecodePayloads(self, event):
        """Perform Base64 decoding on the payloads."""
        try:
            if not self.payloadHandler.encodingStack or self.payloadHandler.encodingStack[-1] != 'base64_encode':
                expected = self.payloadHandler.encodingStack[-1] if self.payloadHandler.encodingStack else "None"
                JOptionPane.showMessageDialog(self.panel, "Decoding not in sequence. Expected encoding: {}".format(expected), "Error", JOptionPane.ERROR_MESSAGE)
                return

            def fix_padding(b64_string):
                return b64_string + '=' * (4 - len(b64_string) % 4) if len(b64_string) % 4 != 0 else b64_string

            selected_text = self.payloadsArea.getSelectedText()
            lines = self.payloadsArea.getText().splitlines()

            if selected_text:
                start = self.payloadsArea.getSelectionStart()
                end = self.payloadsArea.getSelectionEnd()

                updated_lines = []
                for i, line in enumerate(lines):
                    line_start = self.payloadsArea.getLineStartOffset(i)
                    line_end = self.payloadsArea.getLineEndOffset(i)

                    if line_start <= start < line_end or line_start < end <= line_end:
                        padded_text = fix_padding(line)
                        try:
                            decoded_line = base64.b64decode(padded_text).decode("utf-8")
                            updated_lines.append(decoded_line)
                        except Exception:
                            updated_lines.append(line)  # Leave unchanged if invalid
                    else:
                        updated_lines.append(line)

                self.payloadsArea.setText("\n".join(updated_lines))
            else:
                decoded_lines = []
                for line in lines:
                    try:
                        padded_text = fix_padding(line)
                        decoded_lines.append(base64.b64decode(padded_text).decode("utf-8"))
                    except Exception:
                        decoded_lines.append(line)  # Leave unchanged if invalid
                self.payloadsArea.setText("\n".join(decoded_lines))

            self.payloadHandler.encodingStack.pop()
        except Exception as e:
            JOptionPane.showMessageDialog(self.panel, "Error in Base64 decoding: {}".format(str(e)), "Error", JOptionPane.ERROR_MESSAGE)


    def is_valid_url_encoded(self, text):
        """Check if a string is valid URL-encoded data."""
        try:
            URLDecoder.decode(text, StandardCharsets.UTF_8.toString())
            return True  # If decoding succeeds, it's valid
        except Exception:
            return False

    def is_valid_base64(self, text):
        """Check if a string is valid Base64-encoded data."""
        if not text or len(text) % 4 != 0:
            return False
        return re.match("^[A-Za-z0-9+/=]+$", text) is not None

    def getTabCaption(self):
        return "BurpCraft"

    def getUiComponent(self):
        return self.panel

    def getGeneratorName(self):
        return "BurpCraft"

    def createNewInstance(self, attack):
        if self.savedPayloads:
            return PayloadGenerator(self.savedPayloads)
        else:
            selected_heading = self.headingSelector.getSelectedItem()
            if selected_heading == "Select a Payload":
                return PayloadGenerator([])
            elif selected_heading in self.githubPayloads:
                return PayloadGenerator(self.githubPayloads[selected_heading])
            else:
                payloads = [payload for payload in self.payloadsArea.getText().splitlines() if payload.strip()]
                return PayloadGenerator(payloads)


class PayloadGenerator(IIntruderPayloadGenerator):

    def __init__(self, payloads):
        self.payloads = payloads
        self.index = 0

    def hasMorePayloads(self):
        return self.index < len(self.payloads)

    def getNextPayload(self, baseValue):
        if self.index < len(self.payloads):
            payload = self.payloads[self.index]
            self.index += 1
            return payload
        return None

    def reset(self):
        self.index = 0