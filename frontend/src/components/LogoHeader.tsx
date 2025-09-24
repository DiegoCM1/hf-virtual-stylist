import Image from "next/image";

export function LogoHeader() {
  return (
    <header className="mb-6 flex items-center justify-between">
      <Image
        src="/logo-transparent.webp"
        alt="Harris & Frank logo"
        width={180}
        height={60}
        priority
      />
    </header>
  );
}
