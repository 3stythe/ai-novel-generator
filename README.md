# 🤖 ai-novel-generator - Create Novels with Ease

[![Version](https://img.shields.io/badge/version-0.2.1-blue.svg)](https://github.com/Cody8722/ai-novel-generator/releases)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Test](https://img.shields.io/badge/test-passing-success.svg)](docs/reports/STRESS_TEST_REPORT.md)

## 🚀 Getting Started

Welcome to the AI Novel Generator! This tool helps you create long-form novels quickly and at a low cost. Follow these steps to download and run the application.

### 1. Download the Application

Visit the [Releases page](https://github.com/Cody8722/ai-novel-generator/releases) to download the latest version of the software. You can find the executable file there. 

### 2. Install Requirements

Open your command line interface (CLI) and run the following command to install necessary packages:

```bash
pip install -r requirements.txt
```

**Dependencies**:
- `requests>=2.31.0` - For handling HTTP requests.
- `python-dotenv>=1.0.0` - To manage environment variables.

### 3. Set Up Your API Key

You need to configure an API Key to use the novel generator. Create a file named `.env` in the application folder. Add your API Key with the following line:

```bash
SILICONFLOW_API_KEY=your_api_key_here
```

You can obtain your API Key by visiting the [SiliconFlow website](https://siliconflow.cn/).

### 4. Test the Connection

To ensure everything works properly, test your connection to the API by running:

```bash
python novel_generator.py --test-api
```

This command verifies that your setup is correct. If everything is good, you will see a success message.

### 5. Generate Your Novel

Now, you are ready to generate your novel. Run the following command to start an interactive session:

```bash
python novel_generator.py
```

Follow the on-screen instructions to choose topics and set parameters for your novel. 

**Example Input**:
- Topics: `"ai,automated-writing,chinese,creative-writing,machine-learning,nlp,novel-generator,python,qwen,siliconflow,text-generation"`

### 6. Monitor Progress

While your novel is generating, you can monitor the token usage and cost in real-time. The application will provide updates on your current session.

## 🎉 Features

- **Fast Generation**: Create a chapter in roughly 34 seconds.
- **Low Cost**: Generate a 100-chapter novel for only ¥0.24.
- **Coherent Storylines**: Ensure your characters and plot are logically consistent.
- **Error Recovery**: The application automatically retries any failed requests.
- **Real-Time Tracking**: Keep an eye on your token usage and expenses.
- **Customizable Options**: Tailor your novel’s themes, characters, and chapters.

## 📥 Download & Install

To download the latest version, click here: [Release Download](https://github.com/Cody8722/ai-novel-generator/releases). Follow the earlier steps to install it on your device and start creating novels.

For more information, visit the [documentation](https://github.com/Cody8722/ai-novel-generator/docs).

Now you have everything you need to start using the AI Novel Generator. Enjoy creating your stories!