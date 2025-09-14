# 🎨 KalaKarigar.ai

*Empowering Local Artisans with AI*

[![Hackathon](https://img.shields.io/badge/Hackathon-GenAI%20Exchange-blue)](#)
[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-FF4B4B)](https://streamlit.io/)
[![Google Cloud](https://img.shields.io/badge/Powered%20by-Google%20Cloud-yellow)](https://cloud.google.com/)

---

## ✨ Vision

**KalaKarigar.ai** leverages **Google’s Generative AI** to empower Indian craftsmen by automating content creation, enhancing product imagery, and enabling them to build a digital presence — without needing technical expertise.

---

## 🎯 Features (MVP)

* **👤 Onboarding:** Simple artisan profile setup (Name, Craft type, Product image).
* **📝 AI Content Generator:** Gemini-powered product descriptions, captions & hashtags.
* **🎨 Image Enhancement Presets:** Vibrant 🎨 | Studio 🖼️ | Festive ✨.
* **🌐 Deployment:** Hosted on **Google Cloud Run** with optional custom domain **kalakarigar.ai**.

---

## 🏗️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python)
* **Backend & AI:** [Gemini 2.5 Pro](https://ai.google.dev/) via Google AI Studio / Vertex AI
* **Image Processing:** rembg, OpenCV, Pillow
* **Storage:** Firebase (images & artisan data)
* **Deployment:** Google Cloud Run

---

## 📂 Project Structure

```
KalaKarigar.ai/
│── app.py                 # Streamlit main app
│── requirements.txt       # Dependencies
│── utils/
│    ├── ai_utils.py       # Gemini API functions
│    ├── image_utils.py    # Image enhancement presets
│── assets/
│    ├── logo.png          # Team logo
│── README.md              # Project overview
```

---

## ⚡ Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Yash-Kakadiya/KalaKarigar.ai.git
cd KalaKarigar.ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment

Create a `.env` file with your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the app locally

```bash
streamlit run app.py
```

---

## 🚀 Deployment

* Will be deployed on **Google Cloud Run**.
* Optional custom domain: **kalakarigar.ai**.

---

## 📦 Deliverables (Hackathon Submission)

* ✅ Working prototype link (Cloud Run / kalakarigar.ai)
* ✅ Public GitHub repo
* ✅ 3-min demo video
* ✅ Pitch deck

---

## 👨‍💻 Team

**KalaKarigar.ai** – Solo project by Yash (student participant).

---

## 🔮 Future Roadmap

The MVP focuses on onboarding, AI content generation, and image enhancement. Beyond the hackathon, KalaKarigar.ai can be expanded into a comprehensive platform for artisans:

* **🌍 Multi-Language Support:** Add regional languages (Hindi, Tamil, Gujarati, Bengali, etc.) for inclusivity.
* **📊 Analytics Dashboard:** Provide artisans with insights into customer engagement, trending products, and market demand.
* **🛒 E-commerce Integration:** Allow direct sales through KalaKarigar.ai with payment gateway support.
* **🤝 Community Features:** Create artisan communities for collaboration, sharing tips, and mentorship.
* **📸 Advanced Image AI:** Integrate AI-driven background generation, virtual staging, and AR previews.
* **🎥 Video Content Generation:** Help artisans create short promotional videos for platforms like Instagram Reels and YouTube Shorts.
* **🔗 Marketplace Partnerships:** Integrate with established platforms (Etsy, Amazon Karigar) for extended reach.

This roadmap highlights KalaKarigar.ai’s potential to grow into a sustainable ecosystem, ensuring India’s traditional crafts thrive in the digital era.
