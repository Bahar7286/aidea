import { Suspense } from "react";
import VerifyPage from "./VerifyClient";

export default function Page() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center text-sm text-[var(--auth-muted)]">
          Yükleniyor...
        </div>
      }
    >
      <VerifyPage />
    </Suspense>
  );
}
