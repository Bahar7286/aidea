"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, Farm, ManagementZone } from "@/lib/api";

const DEVICE_TYPES = [
  { id: "soil_moisture", label: "Toprak nemi", hint: "Field Node Lite" },
  { id: "weather", label: "Hava istasyonu", hint: "Sıcaklık / nem" },
  { id: "ec", label: "EC sensörü", hint: "İletkenlik" },
  { id: "flow", label: "Debi sensörü", hint: "Vana hattı" },
  { id: "field_node", label: "Field Node", hint: "Modüler node" },
  { id: "other", label: "Diğer", hint: "Genel" },
] as const;

const DEPTHS = [10, 20, 40, 60] as const;
const CONNECTIONS = [
  { id: "wifi", label: "Wi-Fi" },
  { id: "lora", label: "LoRa" },
  { id: "bluetooth", label: "Bluetooth" },
] as const;

export default function NewDevicePage() {
  const params = useParams();
  const router = useRouter();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [zones, setZones] = useState<ManagementZone[]>([]);
  const [step, setStep] = useState(1);
  const [deviceType, setDeviceType] = useState<string>("soil_moisture");
  const [deviceName, setDeviceName] = useState("Toprak Nemi Sensörü");
  const [serial, setSerial] = useState("");
  const [zoneId, setZoneId] = useState<number | "">("");
  const [region, setRegion] = useState("");
  const [depth, setDepth] = useState<number>(20);
  const [connectionType, setConnectionType] = useState("wifi");
  const [sampling, setSampling] = useState(15);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [testOk, setTestOk] = useState(false);

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

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (step < 4) {
      if (step === 1 && (!deviceName.trim() || !deviceType)) {
        setError("Cihaz türü ve adı gerekli.");
        return;
      }
      setError("");
      setStep((s) => s + 1);
      return;
    }
    setLoading(true);
    setError("");
    try {
      const device = await api.createDevice({
        farm_id: farmId,
        device_name: deviceName.trim(),
        device_type: deviceType,
        serial_number: serial.trim() || null,
        zone_id: zoneId === "" ? null : zoneId,
        region_name: region.trim() || null,
        depth_cm: depth,
        connection_type: connectionType,
        sampling_minutes: sampling,
      });
      if (testOk) {
        await api.testDevice(device.id);
      }
      router.push(`/farms/${farmId}/devices/${device.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kayıt başarısız");
    } finally {
      setLoading(false);
    }
  }

  const steps = ["Tür", "Konum", "Ağ", "Onay"];

  return (
    <AppShell title="Yeni Cihaz Bağla" farmName={farm?.name}>
      <div className="mb-6">
        <Link
          href={`/farms/${farmId}/devices`}
          className="text-sm text-[var(--auth-forest)] hover:underline"
        >
          ← Cihaz listesi
        </Link>
      </div>

      <ol className="mb-6 grid grid-cols-4 gap-2">
        {steps.map((label, i) => {
          const n = i + 1;
          const active = step === n;
          const done = step > n;
          return (
            <li
              key={label}
              className={`rounded-xl px-2 py-3 text-center text-xs font-semibold ${
                active
                  ? "bg-[var(--auth-forest)] text-white"
                  : done
                    ? "bg-emerald-50 text-emerald-900"
                    : "bg-white text-[var(--auth-muted)] ring-1 ring-[var(--auth-border)]"
              }`}
            >
              <span className="block text-[10px] opacity-80">{n}</span>
              {label}
            </li>
          );
        })}
      </ol>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      <form
        onSubmit={onSubmit}
        className="grid gap-6 lg:grid-cols-[1fr_260px]"
      >
        <div className="app-surface space-y-4 p-4 sm:p-6">
          {step === 1 && (
            <>
              <p className="text-sm font-semibold">Cihaz türü seçin</p>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                {DEVICE_TYPES.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => {
                      setDeviceType(t.id);
                      if (!deviceName || deviceName.startsWith("Toprak")) {
                        setDeviceName(t.label + " 01");
                      }
                    }}
                    className={`rounded-2xl border p-3 text-left transition ${
                      deviceType === t.id
                        ? "border-[var(--auth-forest)] bg-emerald-50"
                        : "border-[var(--auth-border)] bg-white"
                    }`}
                  >
                    <p className="text-sm font-semibold">{t.label}</p>
                    <p className="text-[11px] text-[var(--auth-muted)]">
                      {t.hint}
                    </p>
                  </button>
                ))}
              </div>
              <div>
                <label className="label" htmlFor="name">
                  Cihaz adı
                </label>
                <input
                  id="name"
                  className="input"
                  value={deviceName}
                  onChange={(e) => setDeviceName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="label" htmlFor="serial">
                  Seri no
                </label>
                <input
                  id="serial"
                  className="input"
                  value={serial}
                  onChange={(e) => setSerial(e.target.value)}
                  placeholder="SN-…"
                />
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <p className="text-sm font-semibold">Konum</p>
              <div>
                <label className="label" htmlFor="zone">
                  Yönetim bölgesi
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
                  placeholder="Kuzey / Batı…"
                />
              </div>
              <div>
                <p className="label">Ölçüm derinliği</p>
                <div className="flex flex-wrap gap-2">
                  {DEPTHS.map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => setDepth(d)}
                      className={`rounded-lg px-3 py-2 text-sm font-semibold ${
                        depth === d
                          ? "bg-[var(--auth-forest)] text-white"
                          : "bg-white ring-1 ring-[var(--auth-border)]"
                      }`}
                    >
                      {d} cm
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <p className="text-sm font-semibold">Ağ / bağlantı</p>
              <div className="flex flex-wrap gap-2">
                {CONNECTIONS.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setConnectionType(c.id)}
                    className={`rounded-lg px-3 py-2 text-sm font-semibold ${
                      connectionType === c.id
                        ? "bg-[var(--auth-forest)] text-white"
                        : "bg-white ring-1 ring-[var(--auth-border)]"
                    }`}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
              <div>
                <label className="label" htmlFor="sampling">
                  Örnekleme (dakika)
                </label>
                <select
                  id="sampling"
                  className="input"
                  value={sampling}
                  onChange={(e) => setSampling(Number(e.target.value))}
                >
                  {[5, 15, 30, 60].map((m) => (
                    <option key={m} value={m}>
                      {m} dakika
                    </option>
                  ))}
                </select>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={testOk}
                  onChange={(e) => setTestOk(e.target.checked)}
                />
                Kayıttan sonra simülasyon bağlantı testi çalıştır
              </label>
              <p className="text-xs text-[var(--auth-muted)]">
                Ağ bilgileri MVP’de saklanmaz; cihaz kaydı simülasyon
                etiketlidir.
              </p>
            </>
          )}

          {step === 4 && (
            <div className="space-y-2 text-sm">
              <p className="font-semibold">Onay özeti</p>
              <ul className="space-y-1 text-[var(--auth-muted)]">
                <li>
                  Ad: <strong className="text-[var(--auth-ink)]">{deviceName}</strong>
                </li>
                <li>
                  Tür:{" "}
                  <strong className="text-[var(--auth-ink)]">{deviceType}</strong>
                </li>
                <li>
                  Derinlik:{" "}
                  <strong className="text-[var(--auth-ink)]">{depth} cm</strong>
                </li>
                <li>
                  Bağlantı:{" "}
                  <strong className="text-[var(--auth-ink)]">
                    {connectionType}
                  </strong>
                </li>
                <li>
                  Kaynak etiketi:{" "}
                  <strong className="text-[var(--auth-ink)]">simulation</strong>
                </li>
              </ul>
            </div>
          )}

          <div className="flex flex-wrap gap-2 pt-2">
            {step > 1 && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setStep((s) => s - 1)}
              >
                Geri
              </button>
            )}
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {step < 4 ? "Devam et" : loading ? "Kaydediliyor…" : "Cihazı kaydet"}
            </button>
          </div>
        </div>

        <aside className="app-surface hidden h-fit space-y-3 p-4 text-sm lg:block">
          <p className="font-semibold">Kurulum ipucu</p>
          <p className="text-xs text-[var(--auth-muted)]">
            Probe’u kök bölgesine yakın, {depth} cm derinlikte yerleştirin. MVP
            cihazları gerçek donanım değildir; Field Node Lite mimarisine göre
            kayıt tutulur.
          </p>
          <Link
            href={`/farms/${farmId}/devices`}
            className="text-xs text-[var(--auth-forest)] hover:underline"
          >
            Listeye dön
          </Link>
        </aside>
      </form>
    </AppShell>
  );
}
