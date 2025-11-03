# Frontend – Next.js App Router

## Descripción General
El frontend es una aplicación Next.js 15 que entrega la experiencia de estilista orientada al cliente y un dashboard administrativo. Se comunica con el servicio FastAPI a través de un proxy `/api/*`, expone metadata de tela y colores, orquesta la generación de imágenes, y permite a los equipos de merchandising curar el inventario desde `/admin`.

## Características Principales
- **Flujo de estilismo guiado** – `useVirtualStylist` obtiene el catálogo, gestiona el estado de selección, dispara generaciones, y mantiene feedback de carga y error consistente a través de los componentes.
- **Experiencia rica de galería** – Componentes como `GeneratedImageGallery`, `ImageModal`, y `LoadingState` proporcionan grids de thumbnails, previsualizaciones con zoom, y feedback de progreso para los looks renderizados.
- **Búsqueda de tela y creación rápida** – La ruta `/admin` renderiza una tabla interactiva que puede buscar, alternar estado activo, y poblar telas demo vía los helpers de API admin en `src/lib/adminApi.ts`.
- **Uploads amigables con dispositivos** – `ImageUploadControls` expone selectores de cámara y galería; las previsualizaciones se muestran con metadata para que los asociados puedan mezclar imágenes de referencia en conversaciones.

## Estructura del Proyecto
```
frontend/
├── src/
│   ├── app/            # Páginas App Router (`page.tsx`, `/admin`)
│   ├── components/     # UI reutilizable (selector catálogo, galería, modals)
│   ├── hooks/          # Máquina de estado `useVirtualStylist`
│   ├── lib/            # Clientes API y helpers tipados
│   └── types/          # Contratos TypeScript compartidos
├── public/             # Assets estáticos (logos)
├── next.config.ts      # Rewrites proxy API y patrones imagen remota
└── package.json        # Scripts y dependencias
```

## Primeros Pasos
1. Instalar dependencias: `npm install`.
2. Crear `.env.local` para apuntar el proxy y tooling admin a tu backend:
   ```env
   NEXT_PUBLIC_API_BASE=http://localhost:8000
   ```
   `next.config.ts` reescribe `/api/:path*` a `NEXT_PUBLIC_API_BASE`, así las llamadas de catálogo y generación van directo a FastAPI manteniendo URLs relativas dentro de la app.
3. Ejecutar servidor de desarrollo: `npm run dev` (por defecto en `http://localhost:3000`).
4. Abrir `/admin` para acceder a la consola de merchandising. Se apoya en el mismo proxy `/api` para requests `GET/POST/PATCH /admin/fabrics`.

## Helpers API
- `fetchCatalog()` y `generateImages()` viven en `src/lib/apiClient.ts` y retornan respuestas tipadas consumidas por el hook y componentes UI.
- Helpers admin (`listFabrics`, `createFabric`, `setFabricStatus`, `deactivateFabric`) usan un cliente Axios configurado con el path base `/api`, haciendo el dashboard portable entre dev local y despliegues RunPod.

## Testing y Calidad
Ejecutar ESLint para detectar problemas de TypeScript y accesibilidad:
```bash
npm run lint
```

## Notas de Despliegue
- Los proxies de Vercel/Next automáticamente reenviarán `/api/*` cuando `NEXT_PUBLIC_API_BASE` esté configurado en el entorno. Para hosting estático o despliegues personalizados, configurar un rewrite equivalente.
- Asegurar que el backend expone URLs de assets HTTPS (o configurar `NEXT_PUBLIC_API_BASE`) para que la galería pueda mostrar imágenes generadas sin advertencias de contenido mixto.
