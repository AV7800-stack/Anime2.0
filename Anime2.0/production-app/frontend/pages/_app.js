import '../styles/globals.css';
import { Toaster } from 'react-hot-toast';
import { authUtils } from '../lib/auth';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

function MyApp({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    // Check authentication on route change
    const handleRouteChange = () => {
      const publicRoutes = ['/login', '/signup', '/'];
      const isPublicRoute = publicRoutes.includes(router.pathname);
      
      if (!isPublicRoute && !authUtils.isAuthenticated()) {
        router.push('/login');
      }
    };

    // Initial check
    handleRouteChange();

    // Listen for route changes
    router.events.on('routeChangeComplete', handleRouteChange);

    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router]);

  return (
    <>
      <Component {...pageProps} />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1f2937',
            color: '#fff',
            border: '1px solid #374151',
          },
          success: {
            style: {
              background: '#10b981',
              color: '#fff',
            },
          },
          error: {
            style: {
              background: '#ef4444',
              color: '#fff',
            },
          },
        }}
      />
    </>
  );
}

export default MyApp;
