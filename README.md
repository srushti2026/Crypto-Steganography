# 🛡️ VeilForge - Advanced Steganography Platform# VeilForge - Advanced Steganography Platform# 🛡️ VeilForge - Advanced Steganography Platform<<<<<<< HEAD



<div align="center">



![VeilForge Logo](frontend/public/logo.png)A modern steganography platform that allows users to hide and extract data from various file formats including images, videos, audio files, and documents.# Supabase CLI



**Hide your secrets in plain sight with cutting-edge steganography technology**



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)## 🏗️ Project Structure<div align="center">

[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)

[![Supabase](https://img.shields.io/badge/Database-Supabase-green.svg)](https://supabase.io/)

This project is organized into two main directories for deployment:[![Coverage Status](https://coveralls.io/repos/github/supabase/cli/badge.svg?branch=main)](https://coveralls.io/github/supabase/cli?branch=main) [![Bitbucket Pipelines](https://img.shields.io/bitbucket/pipelines/supabase-cli/setup-cli/master?style=flat-square&label=Bitbucket%20Canary)](https://bitbucket.org/supabase-cli/setup-cli/pipelines) [![Gitlab Pipeline Status](https://img.shields.io/gitlab/pipeline-status/sweatybridge%2Fsetup-cli?label=Gitlab%20Canary)

[🚀 Live Demo](https://veilforge.vercel.app) • [📖 Documentation](./DEPLOYMENT.md) • [🐛 Report Bug](https://github.com/yourusername/VeilForge/issues)



</div>

```![VeilForge Logo](frontend/public/logo.png)](https://gitlab.com/sweatybridge/setup-cli/-/pipelines)

---

VeilForge/

## 🌟 What is VeilForge?

├── backend/                    # FastAPI Backend (Deploy to Render)

VeilForge is a state-of-the-art steganography platform that allows you to **hide sensitive data inside everyday files** like images, videos, audio files, and documents. Whether you're a security professional, researcher, or privacy enthusiast, VeilForge provides enterprise-grade data concealment capabilities through an intuitive web interface.

│   ├── app.py                  # Main FastAPI application

### ✨ Key Features

│   ├── modules/                # Steganography processing modules**Secure • Professional • Open Source**[Supabase](https://supabase.io) is an open source Firebase alternative. We're building the features of Firebase using enterprise-grade open source tools.

- 🖼️ **Multi-Format Support**: Hide data in images (PNG, JPG, BMP), videos (MP4, AVI, MOV), audio files (WAV, MP3, FLAC), and documents (PDF, DOCX)

- 🔐 **Military-Grade Encryption**: AES-256-GCM encryption with custom passwords│   ├── requirements.txt        # Python dependencies

- 🕵️ **Forensic Mode**: Advanced steganography with metadata embedding for enhanced security

- 📦 **Batch Processing**: Process multiple files simultaneously│   ├── render.yaml            # Render deployment configuration

- 🎯 **Real-Time Progress**: Live status updates and progress tracking

- 🌐 **Modern UI**: Responsive React-based interface with dark/light themes│   ├── database_schema.sql    # Database schemas

- 🔒 **Secure Upload**: Temporary file handling with automatic cleanup

- 📊 **Operation History**: Track all your steganography operations with Supabase integration│   └── README.md              # Backend documentation*Hide sensitive data in plain sight with military-grade steganography*This repository contains all the functionality for Supabase CLI.



---│



## 🎯 How It Works├── frontend/                   # React Frontend (Deploy to Vercel)



### Embedding Process│   ├── src/                   # React source code

1. **Upload Carrier File**: Choose your cover file (image, video, audio, or document)

2. **Select Content**: Either type text or upload a file to hide│   ├── package.json           # Node.js dependencies[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?logo=vercel&logoColor=white)](https://vercel.com)- [x] Running Supabase locally

3. **Set Password**: Create a strong encryption password

4. **Choose Method**: Select standard or forensic embedding mode│   ├── vercel.json            # Vercel deployment configuration

5. **Process**: VeilForge embeds your data invisibly into the carrier file

6. **Download**: Get your steganographically enhanced file│   └── README.md              # Frontend documentation[![React](https://img.shields.io/badge/Frontend-React%2018-61dafb?logo=react)](https://reactjs.org)- [x] Managing database migrations



### Extraction Process  │

1. **Upload File**: Upload a file that contains hidden data

2. **Enter Password**: Provide the decryption password├── .env.template              # Environment variables template[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)- [x] Creating and deploying Supabase Functions

3. **Extract**: VeilForge recovers the hidden content

4. **Download**: Retrieve your original hidden data├── .gitignore                 # Git ignore rules



### 🧪 Example Use Cases└── README.md                  # This file[![Supabase](https://img.shields.io/badge/Database-Supabase-3ecf8e?logo=supabase)](https://supabase.com)- [x] Generating types directly from your database schema



- **Digital Forensics**: Embed investigation metadata in evidence files```

- **Secure Communication**: Hide sensitive messages in innocent-looking images

- **Copyright Protection**: Embed ownership information in media files  [![TypeScript](https://img.shields.io/badge/Code-TypeScript-3178c6?logo=typescript)](https://www.typescriptlang.org)- [x] Making authenticated HTTP requests to [Management API](https://supabase.com/docs/reference/api/introduction)

- **Data Backup**: Store backup keys in multimedia files

- **Privacy Protection**: Conceal personal documents in family photos## 🚀 Deployment

- **Research**: Academic studies on information hiding techniques

[![Python](https://img.shields.io/badge/Code-Python%203.11-3776ab?logo=python)](https://www.python.org)

---

### Backend (Render)

## 🛠️ Technology Stack

1. **Repository**: Connect your GitHub repository to Render[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)## Getting started

### Frontend

- **Framework**: React 18 with TypeScript2. **Root Directory**: Set to `backend`

- **Build Tool**: Vite for fast development and building

- **UI Library**: Tailwind CSS with Radix UI components3. **Build Command**: `pip install -r requirements.txt`

- **State Management**: React Query for server state

- **Deployment**: Vercel for global CDN delivery4. **Start Command**: `uvicorn app:app --host 0.0.0.0 --port 10000`



### Backend  5. **Environment Variables**: Add in Render dashboard (see backend/.env.template)[🚀 **Live Demo**](https://veilforge.vercel.app) • [📖 **Documentation**](#documentation) • [🛠️ **Installation**](#installation) • [🔧 **API Docs**](#api-documentation)### Install the CLI

- **Framework**: FastAPI (Python) for high-performance APIs

- **Processing**: Advanced steganography algorithms with OpenCV, PIL, PyWavelets

- **Database**: Supabase (PostgreSQL) for operation tracking

- **Authentication**: Supabase Auth integration### Frontend (Vercel)

- **Deployment**: Render for scalable backend hosting

1. **Repository**: Connect your GitHub repository to Vercel

### Security

- **Encryption**: AES-256-GCM with PBKDF2 key derivation2. **Root Directory**: Set to `frontend`</div>Available via [NPM](https://www.npmjs.com) as dev dependency. To install:

- **File Handling**: Secure temporary file processing

- **Input Validation**: Comprehensive sanitization and validation3. **Build Command**: `npm run build`

- **Environment Variables**: All secrets secured via environment configuration

4. **Output Directory**: `dist`

---

5. **Environment Variables**: Add in Vercel dashboard (see frontend/.env.template)

## 🚀 Quick Start

---```bash

### Prerequisites

- **Node.js** 18+ and npm## 🔗 Integration

- **Python** 3.8+ with pip

- **Git** for cloning the repositorynpm i supabase --save-dev



### 1. Clone the RepositoryAfter deploying both services:

```bash

git clone https://github.com/yourusername/VeilForge.git1. Update frontend environment variable `VITE_API_URL` with your Render backend URL## 🎯 **What is VeilForge?**```

cd VeilForge

```2. Update backend environment variable `FRONTEND_URL` with your Vercel frontend URL



### 2. Frontend Setup

```bash

cd frontend## 📚 Features

npm install

cp .env.template .envVeilForge is a cutting-edge **steganography platform** that enables secure data hiding within digital media files. Built for cybersecurity professionals, researchers, and privacy advocates, it provides **military-grade encryption** and **undetectable data embedding** across multiple file formats.To install the beta release channel:

# Edit .env with your configuration

npm run dev- **Multi-format Steganography**: Images, videos, audio, documents

```

Frontend will be available at `http://localhost:5173`- **Forensic Mode**: Enhanced security with metadata embedding



### 3. Backend Setup- **Batch Processing**: Multiple files in one operation

```bash

cd ../backend- **Real-time Status**: Operation progress tracking### ✨ **Key Features**```bash

pip install -r requirements.txt

cp .env.template .env  - **Secure Upload**: Temporary file handling with cleanup

# Edit .env with your Supabase credentials

python app.py- **Database Integration**: Operation logging with Supabasenpm i supabase@beta --save-dev

```

Backend API will be available at `http://localhost:8000`- **Modern UI**: React-based responsive interface



### 4. Database Setup (Optional)🔒 **Multi-Format Support**```

If you want full functionality with operation history:

1. Create a [Supabase](https://supabase.io) project## 🔐 Security

2. Run the SQL files in `backend/` to set up tables

3. Add your Supabase credentials to the backend `.env` file- **Images**: PNG, JPEG, GIF, BMP, TIFF



---- Environment variable configuration



## 📱 Screenshots- No hardcoded credentials- **Audio**: WAV, MP3, FLAC, OGGWhen installing with yarn 4, you need to disable experimental fetch with the following nodejs config.



<div align="center">- Secure file upload handling



### Main Interface- Input validation and sanitization- **Video**: MP4, AVI, MOV, WMV

![Main Interface](docs/images/main-interface.png)

- HTTPS recommended for production

### Embedding Process

![Embedding Process](docs/images/embedding-process.png)- **Documents**: PDF, DOCX, TXT```



### Forensic Mode## 📖 Documentation

![Forensic Mode](docs/images/forensic-mode.png)

NODE_OPTIONS=--no-experimental-fetch yarn add supabase

</div>

- Backend API: See `backend/README.md`

---

- Frontend Setup: See `frontend/README.md`🛡️ **Advanced Security**```

## 🔧 Configuration

- Environment Setup: See `.env.template`

### Environment Variables

- **AES-256 Encryption** with password protection

#### Frontend (.env)

```bash## 📄 License

VITE_API_URL=http://localhost:8000          # Backend API URL

VITE_EMAILJS_PUBLIC_KEY=your_key            # EmailJS for contact form- **Digital Signatures** for authenticity verification> **Note**

VITE_EMAILJS_SERVICE_ID=your_service_id     

VITE_EMAILJS_TEMPLATE_ID=your_template_id   See LICENSE file for details.

```- **Metadata Preservation** to avoid suspicionFor Bun versions below v1.0.17, you must add `supabase` as a [trusted dependency](https://bun.sh/guides/install/trusted) before running `bun add -D supabase`.



#### Backend (.env)- **Copyright Protection** with embedded ownership data

```bash

SUPABASE_URL=https://your-project.supabase.co<details>

SUPABASE_KEY=your_supabase_anon_key

FRONTEND_URL=http://localhost:5173          # Frontend URL for CORS⚡ **Professional Tools**  <summary><b>macOS</b></summary>

DEBUG=true                                  # Development mode

```- **Batch Processing** for multiple files



---- **Capacity Analysis** to optimize embedding  Available via [Homebrew](https://brew.sh). To install:



## 🏗️ Project Structure- **Forensic Detection** tools for analysis



```- **API Integration** for enterprise use  ```sh

VeilForge/

├── 🌐 frontend/                 # React Frontend Application  brew install supabase/tap/supabase

│   ├── src/

│   │   ├── components/          # Reusable UI components🌐 **Modern Platform**  ```

│   │   ├── pages/              # Main application pages

│   │   ├── services/           # API integration services- **React + TypeScript** frontend with sleek UI

│   │   └── utils/              # Utility functions

│   ├── public/                 # Static assets- **FastAPI Python** backend for high performance    To install the beta release channel:

│   └── package.json            # Frontend dependencies

│- **Supabase Database** for project management  

├── 🔧 backend/                  # FastAPI Backend Application  

│   ├── app.py                  # Main FastAPI application- **Vercel Deployment** for global accessibility  ```sh

│   ├── modules/                # Steganography processing modules

│   ├── config.py               # Configuration management  brew install supabase/tap/supabase-beta

│   ├── supabase_service.py     # Database integration

│   └── requirements.txt        # Python dependencies---  brew link --overwrite supabase-beta

│

├── 📚 docs/                     # Documentation and guides  ```

├── 🚀 DEPLOYMENT.md            # Detailed deployment instructions

└── 📄 README.md                # This file## 🚀 **Quick Start**  

```

  To upgrade:

---

### **🌍 Try Live Demo**

## 🤝 Contributing

Experience VeilForge instantly: **[veilforge.vercel.app](https://veilforge.vercel.app)**  ```sh

We welcome contributions from the community! Here's how you can help:

  brew upgrade supabase

### Getting Started

1. **Fork** the repository### **💻 Local Development**  ```

2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)

3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)</details>

4. **Push** to the branch (`git push origin feature/AmazingFeature`)

5. **Open** a Pull Request```bash



### Areas for Contribution# 1. Clone repository<details>

- 🐛 **Bug Fixes**: Help us squash bugs and improve stability

- ✨ **New Features**: Implement new steganography algorithms or UI improvements  git clone https://github.com/yourusername/veilforge.git  <summary><b>Windows</b></summary>

- 📚 **Documentation**: Improve guides, add tutorials, or translate content

- 🔍 **Testing**: Add test coverage and improve quality assurancecd veilforge

- 🎨 **Design**: Enhance the user interface and user experience

  Available via [Scoop](https://scoop.sh). To install:

### Development Guidelines

- Follow the existing code style and conventions# 2. Setup environment

- Add tests for new features

- Update documentation for any changescp .env.template .env  ```powershell

- Ensure all tests pass before submitting

# Edit .env with your configuration  scoop bucket add supabase https://github.com/supabase/scoop-bucket.git

---

  scoop install supabase

## 🛡️ Security Considerations

# 3. Start backend  ```

### Best Practices

- **Use Strong Passwords**: Always use complex, unique passwords for encryptionpip install -r requirements.txt

- **Secure Environment**: Keep your `.env` files private and never commit them

- **Regular Updates**: Keep dependencies updated for security patchespython enhanced_app.py  To upgrade:

- **HTTPS Only**: Always use HTTPS in production deployments

- **Input Validation**: The application validates all inputs, but always verify your files



### Responsible Use# 4. Start frontend (new terminal)  ```powershell

VeilForge is designed for legitimate purposes such as:

- ✅ Digital forensics and investigationcd frontend  scoop update supabase

- ✅ Academic research and education  

- ✅ Privacy protection and secure communicationnpm install && npm run dev  ```

- ✅ Copyright and watermarking applications

</details>

Please use this technology responsibly and in compliance with local laws and regulations.

# 5. Access application

---

# Frontend: http://localhost:8080<details>

## 📄 License

# Backend API: http://localhost:8000  <summary><b>Linux</b></summary>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# API Docs: http://localhost:8000/docs

---

```  Available via [Homebrew](https://brew.sh) and Linux packages.

## 🙋‍♂️ Support & Contact



### Getting Help

- 📖 **Documentation**: Check our [deployment guide](./DEPLOYMENT.md)---  #### via Homebrew

- 🐛 **Bug Reports**: [Open an issue](https://github.com/yourusername/VeilForge/issues)

- 💡 **Feature Requests**: [Request a feature](https://github.com/yourusername/VeilForge/issues)

- 💬 **Community**: Join our discussions on GitHub

## 🏗️ **Architecture**  To install:

### Maintainers

- **Lead Developer**: [Your Name](https://github.com/yourusername)

- **Contributors**: See our [contributors page](https://github.com/yourusername/VeilForge/graphs/contributors)

```mermaid  ```sh

---

graph TB  brew install supabase/tap/supabase

## 🌟 Acknowledgments

    A[React Frontend] --> B[FastAPI Backend]  ```

- **Steganography Research**: Built upon decades of academic research in information hiding

- **Open Source Libraries**: Grateful to all the open-source projects that make this possible    B --> C[Supabase Database]

- **Community**: Thanks to all contributors and users who help improve VeilForge

- **Security Community**: Inspired by the need for practical privacy tools    B --> D[Steganography Engine]  To upgrade:



---    D --> E[Image Processing]



<div align="center">    D --> F[Audio Processing]  ```sh



**⭐ If VeilForge helped you, please consider giving it a star! ⭐**    D --> G[Video Processing]  brew upgrade supabase



Made with ❤️ for the privacy and security community    D --> H[Document Processing]  ```



</div>    

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