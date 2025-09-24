type GenerateButtonProps = {
  onClick: () => void;
  disabled: boolean;
  loading: boolean;
};

export function GenerateButton({ onClick, disabled, loading }: GenerateButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full bg-black text-white py-2 rounded disabled:opacity-50 hover:border hover:border-white"
      type="button"
    >
      {loading ? "Generando..." : "Generar imagenes"}
    </button>
  );
}
