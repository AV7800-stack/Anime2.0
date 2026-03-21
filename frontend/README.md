# AI Anime Generator - Frontend

A modern Next.js application for generating anime content with AI.

## Features

- 🎨 Generate anime stories, characters, and scenes
- 📱 Fully responsive design (mobile + desktop)
- 🌙 Beautiful dark theme with anime-inspired UI
- ⚡ Fast performance with Next.js 14
- 🎯 Netflix-like interface

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:3000)

## Deployment

### Vercel Deployment

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`: Your deployed backend URL
4. Deploy!

## Project Structure

```
frontend/
├── app/
│   ├── generate/          # Generation page
│   ├── result/           # Results page
│   ├── globals.css       # Global styles
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Home page
├── components/           # Reusable components
├── .env.example         # Environment variables template
├── next.config.js       # Next.js configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── package.json         # Dependencies
```

## Technologies Used

- **Next.js 14**: React framework
- **Tailwind CSS**: Styling
- **Lucide React**: Icons
- **Axios**: HTTP client
- **TypeScript**: Type safety
