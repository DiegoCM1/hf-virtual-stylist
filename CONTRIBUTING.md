# > Guía de Contribución - HF Virtual Stylist

Gracias por tu interés en contribuir a HF Virtual Stylist. Este documento establece las convenciones, procesos y mejores prácticas para contribuir al proyecto.

---

## =Ë Tabla de Contenidos

1. [Código de Conducta](#código-de-conducta)
2. [Cómo Contribuir](#cómo-contribuir)
3. [Convenciones de Código](#convenciones-de-código)
4. [Proceso de Pull Request](#proceso-de-pull-request)
5. [Commits y Mensajes](#commits-y-mensajes)
6. [Testing](#testing)
7. [Documentación](#documentación)

---

## Código de Conducta

### Principios

- **Respeto:** Trata a todos con profesionalismo y cortesía
- **Colaboración:** Trabaja en equipo, comparte conocimiento
- **Calidad:** Prioriza código mantenible sobre features rápidas
- **Transparencia:** Comunica decisiones y cambios claramente

### Comportamiento Esperado

 Dar feedback constructivo en code reviews
 Hacer preguntas cuando algo no es claro
 Documentar decisiones técnicas importantes
 Reportar bugs con información completa

L Merges sin review
L Commits directos a `main`
L Breaking changes sin discusión
L Código sin tests para features críticos

---

## Cómo Contribuir

### 1. Setup Inicial

Lee y completa [ONBOARDING.md](./ONBOARDING.md) antes de hacer tu primera contribución.

### 2. Encontrar una Tarea

**Issues GitHub:**
- Busca issues etiquetados `good-first-issue` para comenzar
- Comenta en el issue para "reclamarlo" antes de trabajar
- Si no hay issue, créalo primero para discutir el cambio

**Prioridades:**
- =4 **P0 (Critical):** Bugs bloqueantes en producción
- =à **P1 (High):** Features importantes o bugs mayores
- =á **P2 (Medium):** Mejoras incrementales
- =â **P3 (Low):** Nice-to-have, refactors

### 3. Workflow de Desarrollo

```bash
# 1. Actualizar main
git checkout main
git pull origin main

# 2. Crear branch desde main
git checkout -b feature/descripcion-corta
# o
git checkout -b fix/bug-descripcion

# 3. Hacer cambios y commits
git add .
git commit -m "feat: descripción del cambio"

# 4. Push a tu branch
git push origin feature/descripcion-corta

# 5. Abrir Pull Request en GitHub
```

---

## Convenciones de Código

### Backend (Python)

#### Estilo

Seguimos **PEP 8** con algunas excepciones:

```python
#  CORRECTO
def generate_suit_image(
    family_id: str,
    color_id: str,
    seed: int = 123456789,
) -> GeneratedImage:
    """
    Genera imagen de traje usando SDXL.

    Args:
        family_id: Identificador de familia de tela
        color_id: Identificador de color
        seed: Seed para reproducibilidad

    Returns:
        GeneratedImage con URL y metadata

    Raises:
        FabricNotFoundError: Si la tela no existe
    """
    fabric = get_fabric_or_404(family_id, color_id)
    image = self._generate_with_sdxl(fabric, seed)
    return GeneratedImage(url=image.url, seed=seed)


# L INCORRECTO - sin type hints, sin docstring
def generate(fam, col, s=123):
    f = get_fabric(fam, col)
    return do_gen(f, s)
```

#### Convenciones Específicas

**Nombres:**
```python
# Variables/funciones: snake_case
fabric_family = get_fabric_family()
def fetch_catalog(): ...

# Clases: PascalCase
class SdxlTurboGenerator: ...
class FabricFamily: ...

# Constantes: SCREAMING_SNAKE_CASE
DEFAULT_GUIDANCE = 4.3
MAX_RETRIES = 3
```

**Imports:**
```python
# Orden:
# 1. Librerías estándar
import os
from typing import List, Optional

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. Locales
from app.core.config import settings
from app.models.catalog import CatalogResponse
```

**Type Hints:**
```python
#  Siempre usar
def get_fabric(fabric_id: str) -> FabricFamily | None: ...

# L Evitar
def get_fabric(fabric_id): ...
```

**Docstrings:**
```python
#  Google style para funciones públicas
def generate_images(family_id: str, color_id: str) -> list[GeneratedImage]:
    """
    Genera imágenes de traje para una tela y color.

    Args:
        family_id: ID de familia de tela (ej. "algodon-tech")
        color_id: ID de color (ej. "negro-001")

    Returns:
        Lista de GeneratedImage con URLs y metadata

    Raises:
        FabricNotFoundError: Si family_id o color_id no existen
        GenerationError: Si falla la generación SDXL
    """
    ...

# Funciones privadas pueden tener docstring más breve
def _build_prompt(fabric: FabricFamily) -> str:
    """Construye prompt SDXL desde metadata de tela."""
    ...
```

#### Linting

```bash
# Ejecutar antes de commit
cd backend

# Black (formatting automático)
black app/ tests/

# isort (ordenar imports)
isort app/ tests/

# Flake8 (linting)
flake8 app/ tests/

# MyPy (type checking)
mypy app/
```

**Configuración (.flake8):**
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203,W503
```

---

### Frontend (TypeScript)

#### Estilo

Seguimos **Airbnb TypeScript Style Guide** adaptado:

```typescript
//  CORRECTO
interface CatalogSelectorProps {
  families: FabricFamily[];
  selectedFamily: string | null;
  onSelectFamily: (familyId: string) => void;
  isLoading?: boolean;
}

export function CatalogSelector({
  families,
  selectedFamily,
  onSelectFamily,
  isLoading = false,
}: CatalogSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      {families.map((family) => (
        <FamilyCard
          key={family.family_id}
          family={family}
          isSelected={selectedFamily === family.family_id}
          onClick={() => onSelectFamily(family.family_id)}
        />
      ))}
    </div>
  );
}


// L INCORRECTO - sin tipos, inline logic complejo
export function CatalogSelector(props) {
  return (
    <div>
      {props.families.map(f =>
        <div onClick={() => {
          if (f.id !== props.selected) {
            props.onChange(f.id);
          }
        }}>
          {f.name}
        </div>
      )}
    </div>
  );
}
```

#### Convenciones Específicas

**Nombres:**
```typescript
// Componentes: PascalCase
function CatalogSelector() { ... }

// Hooks: camelCase con prefijo "use"
function useVirtualStylist() { ... }

// Funciones/variables: camelCase
const fetchCatalog = async () => { ... }
const isLoading = false;

// Tipos/Interfaces: PascalCase
interface FabricFamily { ... }
type GenerationStatus = 'idle' | 'loading' | 'success' | 'error';

// Constantes: SCREAMING_SNAKE_CASE
const DEFAULT_TIMEOUT = 5000;
```

**Props:**
```typescript
//  Siempre definir interface
interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}

//  Desestructurar con defaults
function Button({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
}: ButtonProps) {
  ...
}

// L Props sin tipo
function Button(props) { ... }
```

**Hooks:**
```typescript
//  Separar lógica en custom hooks
function useVirtualStylist() {
  const [families, setFamilies] = useState<FabricFamily[]>([]);

  useEffect(() => {
    fetchCatalog().then(setFamilies);
  }, []);

  return { families, /* ... */ };
}

// Componente solo renderiza
function HomePage() {
  const { families, selectFamily } = useVirtualStylist();
  return <CatalogSelector families={families} onSelect={selectFamily} />;
}
```

**Async/Await:**
```typescript
//  Manejo de errores explícito
async function generateImages(params: GenerationParams) {
  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to generate images:', error);
    throw error;  // Re-throw para que caller maneje
  }
}

// L Sin manejo de errores
async function generateImages(params) {
  const res = await fetch('/api/generate', { body: params });
  return res.json();
}
```

#### Linting

```bash
cd frontend

# ESLint (linting + some fixes)
npm run lint
npm run lint:fix

# Type checking
npm run type-check
```

**Configuración (.eslintrc.json):**
```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

---

### SQL (Migraciones Alembic)

```python
#  Descriptivo, reversible
def upgrade():
    op.add_column(
        'colors',
        sa.Column('swatch_code', sa.String(100), nullable=True)
    )
    op.create_index(
        'ix_colors_swatch_code',
        'colors',
        ['swatch_code']
    )

def downgrade():
    op.drop_index('ix_colors_swatch_code', 'colors')
    op.drop_column('colors', 'swatch_code')


# L Sin downgrade, sin índice
def upgrade():
    op.add_column('colors', sa.Column('swatch_code', sa.String()))
```

---

## Proceso de Pull Request

### 1. Antes de Abrir PR

**Checklist:**
- [ ] Código sigue convenciones
- [ ] Tests pasan (`pytest` backend, `npm run lint` frontend)
- [ ] Documentación actualizada si aplica
- [ ] Branch actualizado con `main`

```bash
# Actualizar tu branch con main
git checkout main
git pull origin main
git checkout feature/tu-branch
git rebase main  # o git merge main
```

### 2. Abrir Pull Request

**Template de PR:**

```markdown
## Descripción
[Descripción breve del cambio]

## Tipo de Cambio
- [ ] Bug fix (cambio que arregla un issue)
- [ ] Nueva feature (cambio que agrega funcionalidad)
- [ ] Breaking change (fix o feature que causa cambio incompatible)
- [ ] Documentación

## ¿Cómo Ha Sido Testeado?
[Describe las pruebas realizadas]

## Checklist
- [ ] Mi código sigue las convenciones del proyecto
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan nuevos warnings
- [ ] He agregado tests que prueban mi fix/feature
- [ ] Tests nuevos y existentes pasan localmente
```

**Título del PR:**
```
feat: agregar selector de quality preset
fix: corregir error en generación con seed
docs: actualizar ARCHITECTURE.md
refactor: extraer lógica de storage a service
```

### 3. Code Review

**Revisor:**
- Revisar cambios en 24-48 horas
- Dar feedback constructivo y específico
- Aprobar con =M o solicitar cambios

**Autor:**
- Responder a comentarios
- Hacer cambios solicitados
- Re-solicitar review después de cambios

**Ejemplos de feedback:**

 **Constructivo:**
> "En la línea 42, considera usar `dict.get()` en lugar de acceso directo para evitar KeyError si la key no existe."

L **No constructivo:**
> "Esto está mal."

### 4. Merge

**Requisitos para merge:**
-  Mínimo 1 approval de reviewer
-  CI/CD pasa (GitHub Actions si está configurado)
-  Conflictos resueltos
-  Branch actualizado con `main`

**Estrategia de merge:**
- **Squash and merge** (por defecto) - Para features pequeños
- **Rebase and merge** - Para mantener historia limpia
- **Merge commit** - Para features grandes con múltiples commits lógicos

---

## Commits y Mensajes

### Conventional Commits

Formato: `<tipo>(<scope>): <descripción>`

**Tipos:**
- `feat`: Nueva feature
- `fix`: Bug fix
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan código)
- `refactor`: Refactor sin cambiar funcionalidad
- `test`: Agregar o corregir tests
- `chore`: Cambios en build, CI, dependencies

**Ejemplos:**

```bash
#  Buenos commits
git commit -m "feat(backend): agregar endpoint para listar telas activas"
git commit -m "fix(frontend): corregir crash al seleccionar color sin familia"
git commit -m "docs: actualizar README con instrucciones deployment"
git commit -m "refactor(generator): extraer construcción de prompt a método privado"
git commit -m "test(catalog): agregar tests para filtrado de familias"

# L Malos commits
git commit -m "fix stuff"
git commit -m "WIP"
git commit -m "update"
```

### Commits Atómicos

Un commit = un cambio lógico

```bash
#  Separar cambios no relacionados
git add backend/app/routers/catalog.py
git commit -m "feat(catalog): agregar paginación"

git add backend/app/routers/generate.py
git commit -m "fix(generate): validar seed range"

# L Mezclar cambios no relacionados
git add .
git commit -m "varios cambios"
```

---

## Testing

### Backend (Pytest)

**Ubicación:** `backend/tests/`

**Estructura:**
```
tests/
   test_catalog.py      # Tests de endpoints catálogo
   test_generate.py     # Tests de generación
   test_storage.py      # Tests de storage backends
   conftest.py          # Fixtures compartidos
```

**Ejemplo:**
```python
# tests/test_catalog.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_catalog_returns_200():
    response = client.get("/catalog")
    assert response.status_code == 200
    assert "families" in response.json()

def test_get_catalog_includes_active_families_only():
    response = client.get("/catalog")
    families = response.json()["families"]
    assert all(f["status"] == "active" for f in families)
```

**Ejecutar:**
```bash
cd backend
pytest                    # Todos los tests
pytest tests/test_catalog.py  # Un archivo
pytest -v                 # Verbose
pytest --cov=app          # Con coverage
```

### Frontend (Futuro: Vitest)

```typescript
// tests/hooks/useVirtualStylist.test.ts
import { renderHook, act } from '@testing-library/react';
import { useVirtualStylist } from '@/hooks/useVirtualStylist';

describe('useVirtualStylist', () => {
  it('fetches catalog on mount', async () => {
    const { result } = renderHook(() => useVirtualStylist());

    await act(async () => {
      await new Promise(r => setTimeout(r, 100));  // Wait for fetch
    });

    expect(result.current.families).toHaveLength(7);
  });
});
```

---

## Documentación

### Cuándo Actualizar Docs

**Siempre:**
- Nuevos endpoints API ’ Actualizar `backend/README.md`
- Nuevos componentes ’ Agregar JSDoc
- Cambios en arquitectura ’ Actualizar `ARCHITECTURE.md`
- Nuevas variables de entorno ’ Actualizar `.env.example`

**Opcional:**
- Refactors internos (a menos que cambien contratos)
- Bug fixes menores

### Documentación en Código

**Backend:**
```python
#  Docstring para funciones públicas
def generate_suit_images(
    family_id: str,
    color_id: str,
    cuts: list[str],
) -> list[GeneratedImage]:
    """
    Genera renders de traje para una tela/color específicos.

    Esta función orquesta el pipeline completo: carga modelos SDXL,
    aplica ControlNet, genera imágenes, aplica marca de agua, y
    guarda en el backend de almacenamiento configurado.

    Args:
        family_id: ID de familia de tela (ej. "algodon-tech")
        color_id: ID de color (ej. "negro-001")
        cuts: Lista de cortes a generar (["recto", "cruzado"])

    Returns:
        Lista de GeneratedImage con URLs, seeds, y metadata

    Raises:
        FabricNotFoundError: Si family_id o color_id no existen
        GenerationError: Si falla la síntesis SDXL

    Example:
        >>> images = generate_suit_images("algodon-tech", "negro-001", ["recto"])
        >>> assert images[0].url.startswith("https://")
    """
    ...
```

**Frontend:**
```typescript
/**
 * Hook para gestionar estado completo del flujo de estilista.
 *
 * Maneja: catálogo, selección de tela/color, generación de imágenes,
 * y estados de carga/error.
 *
 * @example
 * ```tsx
 * function App() {
 *   const { families, selectFamily, generateImages } = useVirtualStylist();
 *
 *   return (
 *     <CatalogSelector
 *       families={families}
 *       onSelectFamily={selectFamily}
 *     />
 *   );
 * }
 * ```
 */
export function useVirtualStylist() {
  ...
}
```

---

## Preguntas Frecuentes

### ¿Puedo trabajar en múltiples issues a la vez?

Sí, pero usa branches separados. No mezcles cambios no relacionados en un PR.

### ¿Cuándo crear un issue antes de un PR?

- **Siempre** para features nuevos o cambios arquitectónicos
- **Opcional** para bug fixes menores obvios

### ¿Cómo manejo breaking changes?

1. Discutir en issue primero
2. Agregar `BREAKING CHANGE:` en commit message
3. Actualizar documentación completamente
4. Incrementar major version

### ¿Debo escribir tests para todo?

**Prioridades:**
- **Crítico:** Lógica de negocio, endpoints API, utilidades
- **Importante:** Componentes React con lógica
- **Opcional:** Componentes puramente presentacionales

---

## Recursos

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Git Best Practices](https://git-scm.com/book/en/v2)

---

**¿Preguntas?** Abre un issue o pregunta en Slack #hf-virtual-stylist

**¡Gracias por contribuir!** <‰

**Última Actualización:** 2025-11-03
