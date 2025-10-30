import Image from "next/image";

export function LogoHeader() {
  return (
    <header className="w-full py-6 bg-gray-900 rounded-[3px] shadow-md mb-6">
      <div className="flex items-center justify-center">
        <Image
          src="/logo-Harris and frank color blanco.png"
          alt="Harris & Frank logo"
          width={200}
          height={70}
          priority
          className="h-auto"
        />
      </div>
    </header>
  );
}
