import { listFabrics } from "@/lib/adminApi";
import AdminTable from "./AdminTable";

export const dynamic = "force-dynamic"; // no caching; show latest

export default async function AdminPage() {
  const items = await listFabrics({ limit: 50 }); // SSR fetch
  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Admin · Fabrics</h1>
      <AdminTable initialItems={items} />
    </main>
  );
}
