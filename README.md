# 🛠️ **BurpCraft: A Custom Payload Manager for Burp Suite**

**BurpCraft** is a Burp Suite extension designed to simplify your security testing workflow by allowing you to fetch, manage, and customize payloads. Built with Python, this extension integrates seamlessly with Burp Suite using Jython, providing a user-friendly interface to trigger payloads efficiently using Intruder.

---

## 🚀 **Features**

- 🌐 Fetch payloads directly from GitHub for common security testing scenarios.
- ✏️ Customize fetched payloads to meet specific requirements.
- 💾 Save and load your custom payloads for reuse.
- 🔒 Perform encoding (Base64, URL) and decoding operations.

---

## ⚙️ **Installation Instructions**

### 🔗 Prerequisites

Before installing BurpCraft, ensure the following:

- **Burp Suite** (Community or Professional Edition)
- **Jython** (for Python integration with Burp Suite)

---

### Step 1: 🖥️ **Download Jython**

#### For Windows
1. Visit the official [Jython Downloads page](https://www.jython.org/download.html).
2. Download the **Jython installer**.

#### For Linux
1. Visit the official [Jython Downloads page](https://www.jython.org/download.html).
2. Download the **Standalone JAR version** (2.7.4 recommended).

---

### Step 2: 🛠️ **Configure Burp Suite**

1. Open **Burp Suite**.
2. Navigate to **Extensions** > **Extension Settings**.
3. Under **Python Environment**, select the Jython installer (Windows) or the JAR file (Linux).

---

### Step 3: 📥 **Install BurpCraft**

1. Clone or download this repository:
   ```bash
   git clone https://github.com/da0x0/BurpCraft
2. Open Burp Suite.
3. Go to Extensions > Installed.
4. Click the Add button.
5. Select the .py file from this repository.
6. The extension will be added and ready to use.




## 📝 **How to Use BurpCraft**

1. 🔍 **Navigate to the BurpCraft Tab**  
   Open the **BurpCraft** tab in Burp Suite and explore its intuitive GUI designed to streamline your payload management.

2. 🌐 **Fetch Ready-to-Use Payloads**  
   Instantly pull security testing payloads from popular GitHub repositories with a single click.

3. ✏️ **Customize Your Payloads**  
   Tailor the fetched payloads to fit your specific testing scenarios. Add, edit, or tweak them as per your requirements.

4. 💾 **Save Your Creations**  
   Save your customized payloads to reuse them in future testing workflows.

5. 🔓 **Load Saved Payloads**  
   Quickly load previously saved payloads to avoid starting from scratch and accelerate your testing.

6. 🔑 **Encode and Decode Payloads**  
   Perform Base64 and URL encoding/decoding directly within the extension to suit your security testing needs.

7. 🚀 **Deploy in the Intruder Tool**  
   Use your customized payloads with Burp Suite's **Intruder** tool to conduct thorough security assessments.  
   🔥 **Test vulnerabilities** like:  
      - Cross-Site Scripting (XSS)  
      - Directory Traversal  

With **BurpCraft**, you have everything you need to manage payloads and enhance your security testing capabilities—all in one place!

