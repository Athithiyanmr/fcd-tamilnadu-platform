import './globals.css';

export const metadata = {
  title: 'Tamil Nadu FCD Platform',
  description: 'Forest Canopy Density WebGIS for Tamil Nadu',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
