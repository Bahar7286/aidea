"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { FileUp, FileText, Upload } from "lucide-react";
import { AppShell } from "@/components/app/AppShell";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, Farm, LabParameter, ManagementZone } from "@/lib/api";

type PathMode = "report" | "manual";

export default function LabNewPage() {
  const params = useParams();
  const router = useRouter();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [zones, setZones] = useState<ManagementZone[]>([]);
  const [pathMode, setPathMode] = useState<PathMode>("report");
  const [step, setStep] = useState(1);
  const [labName, setLabName] = useState("");
  const [reportNumber, setReportNumber] = useState("");
  const [sampleDate, setSampleDate] = useState("");
  const [depth, setDepth] = useState("20");
  const [zoneId, setZoneId] = useState<number | "">("");
  const [region, setRegion] = useState("");
  const [notes, setNotes] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [originalName, setOriginalName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<number | null>(null);
  const [uploadMsg, setUploadMsg] = useState("");
  const [extractionMode, setExtractionMode] = useState<
    "parsed" | "ai" | "simulated" | "rejected" | "needs_manual" | null
  >(null);
  const [dragOver, setDragOver] = useState(false);
  const [paramsList, setParamsList] = useState<LabParameter[]>([]);
  const [extractionConfidence, setExtractionConfidence] = useState<number | null>(
    null,
  );
  const [soilAccepted, setSoilAccepted] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");
  const [soilGateScore, setSoilGateScore] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    Promise.all([api.getFarm(farmId), api.listZones(farmId)])
      .then(([f, z]) => {
        setFarm(f);
        setZones(z);
      })
      .catch((err) => setError(err.message));
  }, [farmId]);

  async function onFile(file: File | null) {
    if (!file) return;
    if (file.size > 20 * 1024 * 1024) {
      setError("Dosya 20 MB sınırını aşıyor.");
      return;
    }
    setLoading(true);
    setError("");
    setRejectionReason("");
    try {
      const res = await api.uploadLabFile(farmId, file);
      setFileName(res.file_name);
      setOriginalName(res.original_name || file.name);
      setFileSize(res.size_bytes ?? file.size);
      setUploadMsg(res.message);
      setExtractionMode(res.extraction_mode);
      setSoilGateScore(res.soil_gate_score ?? null);
      const ok = !!res.accepted && (res.parameters?.length ?? 0) >= 2;
      setSoilAccepted(ok);
      if (!ok) {
        setParamsList([]);
        setExtractionConfidence(null);
        setRejectionReason(
          res.rejection_reason ||
            res.message ||
            "Bu dosya tarımsal toprak analiz raporu kabul edilmedi.",
        );
        setError(
          res.rejection_reason ||
            res.message ||
            "Toprak laboratuvar raporu değil — doğrulama adımına geçilemez.",
        );
        setStep(1);
        return;
      }
      setParamsList(res.parameters || []);
      setExtractionConfidence(res.extraction_confidence ?? null);
      setPathMode("report");
      setStep(2);
    } catch (err) {
      setSoilAccepted(false);
      setError(err instanceof Error ? err.message : "Yükleme başarısız");
    } finally {
      setLoading(false);
    }
  }

  function startManualPath() {
    setPathMode("manual");
    setFileName(null);
    setOriginalName(null);
    setFileSize(null);
    setExtractionConfidence(null);
    setExtractionMode(null);
    setUploadMsg("");
    setSoilAccepted(true);
    setRejectionReason("");
    setSoilGateScore(null);
    setParamsList([
      { parameter_code: "ph", value: 0, unit: "pH", extracted_auto: false },
      { parameter_code: "ec", value: 0, unit: "dS/m", extracted_auto: false },
      { parameter_code: "om", value: 0, unit: "%", extracted_auto: false },
    ]);
    setStep(2);
  }

  function updateParam(idx: number, field: keyof LabParameter, value: string) {
    setParamsList((prev) =>
      prev.map((r, i) => {
        if (i !== idx) return r;
        if (field === "value") return { ...r, value: Number(value) };
        return { ...r, [field]: value as never };
      }),
    );
  }

  async function saveDraft(e: FormEvent) {
    e.preventDefault();
    if (!labName.trim()) {
      setError("Laboratuvar adı gerekli.");
      return;
    }
    if (pathMode === "report" && !fileName) {
      setError("Rapor yolu için önce dosya yükleyin.");
      return;
    }
    if (pathMode === "report" && !soilAccepted) {
      setError(
        rejectionReason ||
          "Dosya toprak laboratuvar kabul kapısından geçmedi. Doğrulama yok.",
      );
      return;
    }
    const usable = paramsList.filter(
      (p) => p.unit.trim() && Number.isFinite(Number(p.value)),
    );
    if (usable.length === 0) {
      setError("En az bir parametre (değer + birim) gerekli.");
      return;
    }
    if (pathMode === "manual") {
      if (usable.length < 2) {
        setError("Manuel girişte en az iki parametre doldurun (örn. pH + EC).");
        return;
      }
      if (usable.every((p) => Number(p.value) === 0)) {
        setError("Varsayılan sıfırlarla analiz oluşturulamaz. Gerçek değerleri girin.");
        return;
      }
    }
    setLoading(true);
    setError("");
    try {
      const report = await api.createLabReport({
        farm_id: farmId,
        zone_id: zoneId === "" ? null : zoneId,
        lab_name: labName.trim(),
        report_number: reportNumber.trim() || null,
        sample_date: sampleDate ? new Date(sampleDate).toISOString() : null,
        sample_depth_cm: depth,
        sample_region: region.trim() || null,
        file_name: pathMode === "report" ? fileName : null,
        source_type: pathMode === "report" ? "lab_report" : "lab_manual",
        user_confirmed: false,
        notes: notes.trim() || null,
        extraction_confidence:
          pathMode === "report" ? extractionConfidence : null,
        parameters: usable.map((p) => ({
          parameter_code: p.parameter_code,
          value: Number(p.value),
          unit: p.unit,
          extracted_auto: !!p.extracted_auto,
          confidence_pct: p.confidence_pct ?? null,
        })),
      });
      router.push(`/farms/${farmId}/lab/${report.id}/verify`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kayıt başarısız");
    } finally {
      setLoading(false);
    }
  }

  const steps = ["Yükle", "Bilgiler", "Doğrula", "Tamamla"];
  const canContinueReport =
    !!fileName && soilAccepted && paramsList.length >= 2;

  return (
    <AppShell title="Laboratuvar Raporu Yükle" farmName={farm?.name}>
      <div className="mb-4">
        <Link
          href={`/farms/${farmId}/lab`}
          className="text-sm text-[var(--auth-forest)] hover:underline"
        >
          ← Analizler
        </Link>
      </div>

      <ol className="mb-6 grid grid-cols-4 gap-2">
        {steps.map((label, i) => {
          const n = i + 1;
          const active = step === n || (step === 2 && n <= 2);
          return (
            <li
              key={label}
              className={`rounded-xl px-2 py-3 text-center text-xs font-semibold ${
                active
                  ? "bg-[var(--auth-forest)] text-white"
                  : "bg-white text-[var(--auth-muted)] ring-1 ring-[var(--auth-border)]"
              }`}
            >
              {label}
            </li>
          );
        })}
      </ol>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      <form
        onSubmit={saveDraft}
        className="grid gap-6 xl:grid-cols-[1fr_280px]"
      >
        <div className="app-surface space-y-4 p-4 sm:p-6">
          {step === 1 && (
            <>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className={`btn text-sm ${pathMode === "report" ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => setPathMode("report")}
                >
                  Rapor yükle
                </button>
                <button
                  type="button"
                  className={`btn text-sm ${pathMode === "manual" ? "btn-primary" : "btn-secondary"}`}
                  onClick={startManualPath}
                >
                  Manuel lab girişi
                </button>
              </div>

              {pathMode === "report" && (
                <>
                  <div
                    className={`rounded-2xl border-2 border-dashed px-4 py-10 text-center transition ${
                      dragOver
                        ? "border-emerald-500 bg-emerald-50"
                        : "border-[var(--auth-border)] bg-slate-50/80"
                    }`}
                    onDragOver={(e) => {
                      e.preventDefault();
                      setDragOver(true);
                    }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setDragOver(false);
                      onFile(e.dataTransfer.files?.[0] || null);
                    }}
                  >
                    <Upload
                      className="mx-auto h-10 w-10 text-emerald-700"
                      strokeWidth={2}
                      aria-hidden
                    />
                    <p className="mt-3 text-sm font-semibold">
                      Rapor dosyanızı sürükleyin veya seçin
                    </p>
                    <p className="mt-1 text-xs text-[var(--auth-muted)]">
                      Yalnızca tarımsal toprak analiz raporları kabul edilir
                      (pH, organik madde, P2O5, K2O, EC…). PDF, CSV veya TXT
                      (maks. 20 MB). Fatura / rastgele PDF reddedilir; sahte
                      analiz üretilmez. OpenRouter anahtarı varsa AI ayrıştırır.
                    </p>
                    <label className="btn btn-primary mt-4 inline-flex cursor-pointer text-sm">
                      <FileUp className="h-4 w-4" aria-hidden />
                      Dosya seç
                      <input
                        type="file"
                        className="hidden"
                        accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls,.csv,.txt,.tsv"
                        onChange={(e) => onFile(e.target.files?.[0] || null)}
                      />
                    </label>
                    {fileName && (
                      <div className="mx-auto mt-4 flex max-w-md items-start gap-3 rounded-xl bg-white p-3 text-left ring-1 ring-emerald-200">
                        <FileText
                          className="mt-0.5 h-5 w-5 shrink-0 text-emerald-700"
                          aria-hidden
                        />
                        <div className="min-w-0 text-xs">
                          <p className="truncate font-semibold text-emerald-900">
                            {originalName || fileName}
                          </p>
                          <p className="text-[var(--auth-muted)]">
                            Sunucu: {fileName}
                            {fileSize != null
                              ? ` · ${(fileSize / 1024).toFixed(1)} KB`
                              : ""}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                  {rejectionReason && (
                    <div className="rounded-xl bg-red-50 px-3 py-3 text-sm text-red-900 ring-1 ring-red-200">
                      <p className="font-semibold">Rapor kabul edilmedi</p>
                      <p className="mt-1 text-xs">{rejectionReason}</p>
                      {soilGateScore != null && (
                        <p className="mt-1 text-xs text-red-800/80">
                          Toprak benzerlik skoru: {soilGateScore}/100
                        </p>
                      )}
                    </div>
                  )}
                  <button
                    type="button"
                    className="btn btn-primary"
                    disabled={loading || !canContinueReport}
                    onClick={() => setStep(2)}
                  >
                    {loading
                      ? "…"
                      : canContinueReport
                        ? "Bilgilere devam →"
                        : "Önce geçerli toprak raporu yükleyin"}
                  </button>
                  {uploadMsg && !rejectionReason && (
                    <p className="text-xs text-[var(--auth-muted)]">{uploadMsg}</p>
                  )}
                </>
              )}
            </>
          )}

          {step === 2 && (
            <>
              <p className="text-sm font-semibold">
                {pathMode === "report" ? "Rapor bilgileri" : "Manuel lab girişi"}
              </p>
              {pathMode === "report" && fileName && (
                <p className="rounded-xl bg-emerald-50 px-3 py-2 text-xs text-emerald-900">
                  Yüklenen dosya: {originalName || fileName}
                  {extractionMode
                    ? ` · çıkarım: ${
                        extractionMode === "ai"
                          ? "OpenRouter AI"
                          : extractionMode === "parsed"
                            ? "metin"
                            : extractionMode
                      }`
                    : ""}
                  {soilGateScore != null ? ` · skor ${soilGateScore}` : ""}
                </p>
              )}
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="label" htmlFor="lab">
                    Laboratuvar adı *
                  </label>
                  <input
                    id="lab"
                    className="input"
                    value={labName}
                    onChange={(e) => setLabName(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="label" htmlFor="no">
                    Rapor no
                  </label>
                  <input
                    id="no"
                    className="input"
                    value={reportNumber}
                    onChange={(e) => setReportNumber(e.target.value)}
                  />
                </div>
                <div>
                  <label className="label" htmlFor="date">
                    Numune tarihi
                  </label>
                  <input
                    id="date"
                    type="date"
                    className="input"
                    value={sampleDate}
                    onChange={(e) => setSampleDate(e.target.value)}
                  />
                </div>
                <div>
                  <label className="label" htmlFor="depth">
                    Derinlik (cm)
                  </label>
                  <select
                    id="depth"
                    className="input"
                    value={depth}
                    onChange={(e) => setDepth(e.target.value)}
                  >
                    {["0-20", "20", "20-40", "40"].map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label" htmlFor="zone">
                    Bölge
                  </label>
                  <select
                    id="zone"
                    className="input"
                    value={zoneId}
                    onChange={(e) =>
                      setZoneId(e.target.value ? Number(e.target.value) : "")
                    }
                  >
                    <option value="">Seçilmedi</option>
                    {zones.map((z) => (
                      <option key={z.id} value={z.id}>
                        {z.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label" htmlFor="region">
                    Bölge adı
                  </label>
                  <input
                    id="region"
                    className="input"
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <label className="label" htmlFor="notes">
                  Notlar
                </label>
                <textarea
                  id="notes"
                  className="input min-h-[80px]"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <p className="text-xs font-semibold text-[var(--auth-ink)]">
                  Taslak parametreler (onay adımında kesinleşir)
                </p>
                {paramsList.map((p, idx) => (
                  <div
                    key={`${p.parameter_code}-${idx}`}
                    className="grid grid-cols-[1fr_100px_90px] gap-2"
                  >
                    <input
                      className="input py-1.5 text-xs uppercase"
                      value={p.parameter_code}
                      onChange={(e) =>
                        updateParam(idx, "parameter_code", e.target.value)
                      }
                      required
                    />
                    <input
                      className="input py-1.5"
                      type="number"
                      step="0.01"
                      value={p.value}
                      onChange={(e) => updateParam(idx, "value", e.target.value)}
                      required
                    />
                    <input
                      className="input py-1.5"
                      value={p.unit}
                      onChange={(e) => updateParam(idx, "unit", e.target.value)}
                      required
                    />
                  </div>
                ))}
              </div>

              {extractionConfidence != null && pathMode === "report" && (
                <p className="rounded-xl bg-sky-50 px-3 py-2 text-xs text-sky-900">
                  Çıkarım güveni: %{extractionConfidence}
                  {extractionMode === "ai"
                    ? " — OpenRouter AI (şema doğrulamalı); otomatik kayıt yok"
                    : extractionMode === "simulated"
                      ? " — simüle (kullanımdan kaldırıldı)"
                      : " — metin heuristiği; otomatik doğru sayılmaz"}
                  .
                </p>
              )}
              <p className="text-xs text-[var(--auth-muted)]">
                {paramsList.length} parametre taslak; sonraki adımda doğrulayacaksınız.
                AI yorumu yalnızca onaydan sonra.
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setStep(1)}
                >
                  Geri
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={
                    loading ||
                    (pathMode === "report" && (!fileName || !soilAccepted)) ||
                    !labName.trim()
                  }
                >
                  {loading ? "…" : "Kaydet ve doğrula →"}
                </button>
              </div>
            </>
          )}
        </div>

        <aside className="app-surface hidden h-fit space-y-2 p-4 text-xs text-[var(--auth-muted)] xl:block">
          <p className="text-sm font-semibold text-[var(--auth-ink)]">
            Yükleme rehberi
          </p>
          <p>
            Rapor yolu: yalnızca tarımsal toprak laboratuvar raporu. pH, OM,
            P/K zorunlu benzerlik; fatura ve rastgele PDF reddedilir.
          </p>
          <p>
            OPENROUTER_API_KEY varsa metin AI ile JSON parametrelere ayrıştırılır;
            yoksa heuristik. Onaysız kayıt doğrulanmış sayılmaz. Lab verisi IoT
            nem ölçümünün yerini tutmaz.
          </p>
        </aside>
      </form>
    </AppShell>
  );
}
