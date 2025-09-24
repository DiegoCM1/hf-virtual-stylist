export function LoadingState() {
  return (
    <div className="border rounded p-6 text-neutral-600 space-y-2">
      <div className="animate-pulse text-white">Inicializando modelo…</div>
      <div className="animate-pulse text-white">Aplicando textura de tela…</div>
      <div className="animate-pulse text-white">Renderizando vistas recto y cruzado…</div>
    </div>
  );
}
