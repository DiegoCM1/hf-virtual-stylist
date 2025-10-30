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
      className="
        w-full bg-gray-900 text-white
        px-6 py-4 rounded-[3px]
        font-body text-sm font-medium tracking-wide uppercase
        shadow-sm
        transition-all duration-200
        hover:bg-gray-800 hover:shadow-md hover:-translate-y-0.5
        active:translate-y-0
        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-sm
        focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2
      "
      type="button"
    >
      {loading ? (
        <span className="flex items-center justify-center gap-2">
          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Generando...
        </span>
      ) : (
        "Generar Imágenes"
      )}
    </button>
  );
}
