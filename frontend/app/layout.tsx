import './globals.css'
import { Inter } from 'next/font/google'
import { ModalProvider } from '@/components/Modal'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AI Anime Generator',
  description: 'Generate amazing anime stories, images, and videos with AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ModalProvider>
          {children}
        </ModalProvider>
      </body>
    </html>
  )
}
