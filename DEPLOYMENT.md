# VeilForge - Advanced Steganography Platform# 🛡️ VeilForge - Advanced Steganography Platform<<<<<<< HEAD



A modern steganography platform that allows users to hide and extract data from various file formats including images, videos, audio files, and documents.# Supabase CLI



## 🏗️ Project Structure<div align="center">



This project is organized into two main directories for deployment:[![Coverage Status](https://coveralls.io/repos/github/supabase/cli/badge.svg?branch=main)](https://coveralls.io/github/supabase/cli?branch=main) [![Bitbucket Pipelines](https://img.shields.io/bitbucket/pipelines/supabase-cli/setup-cli/master?style=flat-square&label=Bitbucket%20Canary)](https://bitbucket.org/supabase-cli/setup-cli/pipelines) [![Gitlab Pipeline Status](https://img.shields.io/gitlab/pipeline-status/sweatybridge%2Fsetup-cli?label=Gitlab%20Canary)



```![VeilForge Logo](frontend/public/logo.png)](https://gitlab.com/sweatybridge/setup-cli/-/pipelines)

VeilForge/

├── backend/                    # FastAPI Backend (Deploy to Render)

│   ├── app.py                  # Main FastAPI application

│   ├── modules/                # Steganography processing modules**Secure • Professional • Open Source**[Supabase](https://supabase.io) is an open source Firebase alternative. We're building the features of Firebase using enterprise-grade open source tools.

│   ├── requirements.txt        # Python dependencies

│   ├── render.yaml            # Render deployment configuration

│   ├── database_schema.sql    # Database schemas

│   └── README.md              # Backend documentation*Hide sensitive data in plain sight with military-grade steganography*This repository contains all the functionality for Supabase CLI.

│

├── frontend/                   # React Frontend (Deploy to Vercel)

│   ├── src/                   # React source code

│   ├── package.json           # Node.js dependencies[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?logo=vercel&logoColor=white)](https://vercel.com)- [x] Running Supabase locally

│   ├── vercel.json            # Vercel deployment configuration

│   └── README.md              # Frontend documentation[![React](https://img.shields.io/badge/Frontend-React%2018-61dafb?logo=react)](https://reactjs.org)- [x] Managing database migrations

│

├── .env.template              # Environment variables template[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)- [x] Creating and deploying Supabase Functions

├── .gitignore                 # Git ignore rules

└── README.md                  # This file[![Supabase](https://img.shields.io/badge/Database-Supabase-3ecf8e?logo=supabase)](https://supabase.com)- [x] Generating types directly from your database schema

```

[![TypeScript](https://img.shields.io/badge/Code-TypeScript-3178c6?logo=typescript)](https://www.typescriptlang.org)- [x] Making authenticated HTTP requests to [Management API](https://supabase.com/docs/reference/api/introduction)

## 🚀 Deployment

[![Python](https://img.shields.io/badge/Code-Python%203.11-3776ab?logo=python)](https://www.python.org)

### Backend (Render)

1. **Repository**: Connect your GitHub repository to Render[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)## Getting started

2. **Root Directory**: Set to `backend`

3. **Build Command**: `pip install -r requirements.txt`

4. **Start Command**: `uvicorn app:app --host 0.0.0.0 --port 10000`

5. **Environment Variables**: Add in Render dashboard (see backend/.env.template)[🚀 **Live Demo**](https://veilforge.vercel.app) • [📖 **Documentation**](#documentation) • [🛠️ **Installation**](#installation) • [🔧 **API Docs**](#api-documentation)### Install the CLI



### Frontend (Vercel)

1. **Repository**: Connect your GitHub repository to Vercel

2. **Root Directory**: Set to `frontend`</div>Available via [NPM](https://www.npmjs.com) as dev dependency. To install:

3. **Build Command**: `npm run build`

4. **Output Directory**: `dist`

5. **Environment Variables**: Add in Vercel dashboard (see frontend/.env.template)

---```bash

## 🔗 Integration

npm i supabase --save-dev

After deploying both services:

1. Update frontend environment variable `VITE_API_URL` with your Render backend URL## 🎯 **What is VeilForge?**```

2. Update backend environment variable `FRONTEND_URL` with your Vercel frontend URL



## 📚 Features

VeilForge is a cutting-edge **steganography platform** that enables secure data hiding within digital media files. Built for cybersecurity professionals, researchers, and privacy advocates, it provides **military-grade encryption** and **undetectable data embedding** across multiple file formats.To install the beta release channel:

- **Multi-format Steganography**: Images, videos, audio, documents

- **Forensic Mode**: Enhanced security with metadata embedding

- **Batch Processing**: Multiple files in one operation

- **Real-time Status**: Operation progress tracking### ✨ **Key Features**```bash

- **Secure Upload**: Temporary file handling with cleanup

- **Database Integration**: Operation logging with Supabasenpm i supabase@beta --save-dev

- **Modern UI**: React-based responsive interface

🔒 **Multi-Format Support**```

## 🔐 Security

- **Images**: PNG, JPEG, GIF, BMP, TIFF

- Environment variable configuration

- No hardcoded credentials- **Audio**: WAV, MP3, FLAC, OGGWhen installing with yarn 4, you need to disable experimental fetch with the following nodejs config.

- Secure file upload handling

- Input validation and sanitization- **Video**: MP4, AVI, MOV, WMV

- HTTPS recommended for production

- **Documents**: PDF, DOCX, TXT```

## 📖 Documentation

NODE_OPTIONS=--no-experimental-fetch yarn add supabase

- Backend API: See `backend/README.md`

- Frontend Setup: See `frontend/README.md`🛡️ **Advanced Security**```

- Environment Setup: See `.env.template`

- **AES-256 Encryption** with password protection

## 📄 License

- **Digital Signatures** for authenticity verification> **Note**

See LICENSE file for details.
- **Metadata Preservation** to avoid suspicionFor Bun versions below v1.0.17, you must add `supabase` as a [trusted dependency](https://bun.sh/guides/install/trusted) before running `bun add -D supabase`.

- **Copyright Protection** with embedded ownership data

<details>

⚡ **Professional Tools**  <summary><b>macOS</b></summary>

- **Batch Processing** for multiple files

- **Capacity Analysis** to optimize embedding  Available via [Homebrew](https://brew.sh). To install:

- **Forensic Detection** tools for analysis

- **API Integration** for enterprise use  ```sh

  brew install supabase/tap/supabase

🌐 **Modern Platform**  ```

- **React + TypeScript** frontend with sleek UI

- **FastAPI Python** backend for high performance    To install the beta release channel:

- **Supabase Database** for project management  

- **Vercel Deployment** for global accessibility  ```sh

  brew install supabase/tap/supabase-beta

---  brew link --overwrite supabase-beta

  ```

## 🚀 **Quick Start**  

  To upgrade:

### **🌍 Try Live Demo**

Experience VeilForge instantly: **[veilforge.vercel.app](https://veilforge.vercel.app)**  ```sh

  brew upgrade supabase

### **💻 Local Development**  ```

</details>

```bash

# 1. Clone repository<details>

git clone https://github.com/yourusername/veilforge.git  <summary><b>Windows</b></summary>

cd veilforge

  Available via [Scoop](https://scoop.sh). To install:

# 2. Setup environment

cp .env.template .env  ```powershell

# Edit .env with your configuration  scoop bucket add supabase https://github.com/supabase/scoop-bucket.git

  scoop install supabase

# 3. Start backend  ```

pip install -r requirements.txt

python enhanced_app.py  To upgrade:



# 4. Start frontend (new terminal)  ```powershell

cd frontend  scoop update supabase

npm install && npm run dev  ```

</details>

# 5. Access application

# Frontend: http://localhost:8080<details>

# Backend API: http://localhost:8000  <summary><b>Linux</b></summary>

# API Docs: http://localhost:8000/docs

```  Available via [Homebrew](https://brew.sh) and Linux packages.



---  #### via Homebrew



## 🏗️ **Architecture**  To install:



```mermaid  ```sh

graph TB  brew install supabase/tap/supabase

    A[React Frontend] --> B[FastAPI Backend]  ```

    B --> C[Supabase Database]

    B --> D[Steganography Engine]  To upgrade:

    D --> E[Image Processing]

    D --> F[Audio Processing]  ```sh

    D --> G[Video Processing]  brew upgrade supabase

    D --> H[Document Processing]  ```

    

    style A fill:#61dafb,stroke:#333,color:#000  #### via Linux packages

    style B fill:#009688,stroke:#333,color:#fff

    style C fill:#3ecf8e,stroke:#333,color:#fff  Linux packages are provided in [Releases](https://github.com/supabase/cli/releases). To install, download the `.apk`/`.deb`/`.rpm`/`.pkg.tar.zst` file depending on your package manager and run the respective commands.

    style D fill:#ff6b6b,stroke:#333,color:#fff

```  ```sh

  sudo apk add --allow-untrusted <...>.apk

### **Technology Stack**  ```



**Frontend**: React 18 + TypeScript + Vite + TailwindCSS + ShadCN/UI    ```sh

**Backend**: FastAPI + Python 3.11 + NumPy + OpenCV + Cryptography    sudo dpkg -i <...>.deb

**Database**: Supabase (PostgreSQL) with real-time features    ```

**Deployment**: Vercel serverless with global CDN  

  ```sh

---  sudo rpm -i <...>.rpm

  ```

## 🔧 **Core API Endpoints**

  ```sh

```http  sudo pacman -U <...>.pkg.tar.zst

POST /api/embed-data          # Hide data in carrier files  ```

POST /api/extract-data        # Extract hidden data</details>

GET  /api/analyze-capacity    # Check embedding capacity

POST /api/generate-password   # Create secure passwords<details>

GET  /api/projects            # Manage steganography projects  <summary><b>Other Platforms</b></summary>

```

  You can also install the CLI via [go modules](https://go.dev/ref/mod#go-install) without the help of package managers.

**Example Usage**:

```python  ```sh

import requests  go install github.com/supabase/cli@latest

  ```

# Embed secret document in image

files = {  Add a symlink to the binary in `$PATH` for easier access:

    'carrier_file': open('image.png', 'rb'),

    'secret_file': open('document.pdf', 'rb')  ```sh

}  ln -s "$(go env GOPATH)/bin/cli" /usr/bin/supabase

data = {'password': 'secure123', 'encryption': True}  ```



response = requests.post('https://veilforge.vercel.app/api/embed-data',   This works on other non-standard Linux distros.

                        files=files, data=data)</details>

```

<details>

---  <summary><b>Community Maintained Packages</b></summary>



## ⚙️ **Configuration**  Available via [pkgx](https://pkgx.sh/). Package script [here](https://github.com/pkgxdev/pantry/blob/main/projects/supabase.com/cli/package.yml).

  To install in your working directory:

### **Environment Variables**

  ```bash

```bash  pkgx install supabase

# Supabase Database  ```

SUPABASE_URL=https://your-project.supabase.co

SUPABASE_KEY=your-supabase-anon-key  Available via [Nixpkgs](https://nixos.org/). Package script [here](https://github.com/NixOS/nixpkgs/blob/master/pkgs/development/tools/supabase-cli/default.nix).

</details>

# EmailJS (Frontend Contact Forms)

VITE_EMAILJS_PUBLIC_KEY=your-emailjs-key### Run the CLI

VITE_EMAILJS_SERVICE_ID=service_id

VITE_EMAILJS_TEMPLATE_ID=template_id```bash

supabase bootstrap

# SMTP Email (Backend - Optional)```

EMAIL_USER=your-email@gmail.com

EMAIL_PASSWORD=your-app-passwordOr using npx:

RECIPIENT_EMAIL=notifications@yourdomain.com

``````bash

npx supabase bootstrap

### **Database Setup**```



1. Create [Supabase](https://supabase.com) account and projectThe bootstrap command will guide you through the process of setting up a Supabase project using one of the [starter](https://github.com/supabase-community/supabase-samples/blob/main/samples.json) templates.

2. Copy URL and anon key from Settings > API

3. Run database initialization:## Docs

   ```bash

   python setup_database.pyCommand & config reference can be found [here](https://supabase.com/docs/reference/cli/about).

   ```

## Breaking changes

---

We follow semantic versioning for changes that directly impact CLI commands, flags, and configurations.

## 🔒 **Security Features**

However, due to dependencies on other service images, we cannot guarantee that schema migrations, seed.sql, and generated types will always work for the same CLI major version. If you need such guarantees, we encourage you to pin a specific version of CLI in package.json.

- **🛡️ AES-256-GCM Encryption**: Military-grade security

- **🔑 PBKDF2 Key Derivation**: 100,000 iterations for password hashing## Developing

- **✅ HMAC-SHA256**: Message authentication codes  

- **🕵️ LSB Steganography**: Undetectable embedding techniquesTo run from source:

- **📋 Metadata Preservation**: Maintain file authenticity

- **🔍 Integrity Verification**: SHA-256 checksums and digital signatures```sh

# Go >= 1.22

---go run . help

```

## 📊 **Performance Specifications**=======

# MM0

| File Type | Max Size | Processing Time | Embedding Capacity |>>>>>>> afcb080ef88b9edc6e452a793fb93c3da4e57323

|-----------|----------|-----------------|-------------------|
| **Images** | 50 MB | 2-5 seconds | ~12.5% of carrier |
| **Audio** | 100 MB | 5-10 seconds | ~6.25% of carrier |
| **Video** | 500 MB | 15-30 seconds | ~3.125% of carrier |
| **Documents** | 25 MB | 1-3 seconds | ~25% of carrier |

**Deployment Features**:
- ⚡ **Serverless Architecture**: Auto-scaling with demand
- 🌍 **Global CDN**: Sub-second response times worldwide
- 🔄 **Async Processing**: Non-blocking file operations
- 💾 **Memory Optimization**: Efficient streaming for large files

---

## 🚀 **Deployment**

### **Vercel (Recommended)**
1. Fork this repository
2. Connect to [Vercel](https://vercel.com)
3. Set environment variables in dashboard
4. Deploy automatically on push

### **Docker**
```bash
# Build and run container
docker build -t veilforge .
docker run -p 8080:8080 -e SUPABASE_URL=... veilforge
```

### **Manual Server**
```bash
# Production deployment
pip install -r requirements.txt
cd frontend && npm run build
python -m uvicorn enhanced_app:app --host 0.0.0.0 --port 8000
```

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

**Quick Start**:
```bash
# 1. Fork and clone
git clone https://github.com/yourusername/veilforge.git

# 2. Create feature branch  
git checkout -b feature/amazing-feature

# 3. Make changes and test
python -m pytest tests/
npm test --prefix frontend

# 4. Submit pull request
```

**Development Standards**:
- Python: PEP 8 + type hints
- TypeScript: ESLint + Prettier
- Tests: >90% coverage required
- Documentation: Update for new features

---

## 📄 **License**

VeilForge is open-source software licensed under the [MIT License](LICENSE).

**Legal Notice**: This software is for educational, research, and legitimate security purposes. Users must comply with applicable laws and regulations.

---

## 📞 **Support**

- **📖 Documentation**: [GitHub Wiki](https://github.com/yourusername/veilforge/wiki)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/yourusername/veilforge/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/veilforge/discussions)
- **📧 Contact**: [contact@veilforge.com](mailto:contact@veilforge.com)
- **🏢 Enterprise**: [enterprise@veilforge.com](mailto:enterprise@veilforge.com)

---

## 🙏 **Acknowledgments**

Special thanks to the OpenCV, FastAPI, React, Supabase, and Vercel communities for their excellent tools and platforms.

---

<div align="center">

### **🚀 Ready to Hide in Plain Sight?**

**[🌍 Try VeilForge Live](https://veilforge.vercel.app)** • **[⭐ Star on GitHub](https://github.com/yourusername/veilforge)**

---

**Made with ❤️ for Privacy and Security**

*Empowering secure communication through advanced steganography*

</div>