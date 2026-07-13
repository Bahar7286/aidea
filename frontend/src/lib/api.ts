const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type User = {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  role: string;
  email_verified?: boolean;
  is_active?: boolean;
  last_login_at?: string | null;
};

export type AdminOverview = {
  total_users: number;
  active_users: number;
  admin_users: number;
  total_farms: number;
  active_farms: number;
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  avg_soil_moisture: number | null;
  open_tickets: number;
  system_health_pct: number;
  recent_alerts: Array<{ title: string; severity: string; message: string }>;
  recent_activity: string[];
  note: string;
};

export type AdminUser = {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  farm_count: number;
  last_login_at: string | null;
  created_at: string | null;
};

export type AdminFarm = {
  id: number;
  name: string;
  location: string | null;
  area: number | null;
  soil_type: string | null;
  is_active: boolean;
  owner_id: number;
  owner_name: string;
  owner_email: string;
  device_count: number;
  zone_count: number;
  created_at: string | null;
};

export type AdminDevice = {
  id: number;
  farm_id: number;
  farm_name: string;
  device_name: string;
  device_type: string;
  serial_number: string | null;
  connection_status: string;
  battery_percent: number | null;
  signal_dbm: number | null;
  last_data_time: string | null;
  last_moisture: number | null;
  calibration_due: boolean;
};

export type SupportTicket = {
  id: number;
  ticket_no: string;
  user_id: number | null;
  subject: string;
  description: string | null;
  priority: string;
  status: string;
  farm_id: number | null;
  created_at: string;
  updated_at: string;
};

export type AdminBilling = {
  plan: string;
  status: string;
  farms_used: number;
  farms_limit: number;
  devices_used: number;
  devices_limit: number | null;
  storage_used_gb: number;
  storage_limit_gb: number;
  ai_queries_used: number;
  ai_queries_limit: number;
  plans: Array<Record<string, unknown>>;
  invoices: Array<Record<string, unknown>>;
  note: string;
};

export type AdminAnalytics = {
  avg_moisture: number | null;
  avg_temperature: number | null;
  irrigation_events: number;
  predictions: number;
  lab_reports: number;
  moisture_series: Array<{ date: string; avg: number }>;
  water_by_day: Array<{ date: string; liters: number }>;
  feature_usage: Array<{ feature: string; count: number }>;
  note: string;
};

export type AdminSettings = {
  settings: Record<string, string>;
  integrations: Array<{ name: string; status: string; connected: boolean }>;
  note: string;
};

export type RegisterPending = {
  email: string;
  message: string;
  demo_code?: string | null;
  expires_in_seconds: number;
};

export type MessageOut = {
  message: string;
  demo_code?: string | null;
  email?: string | null;
};

export type Farm = {
  id: number;
  name: string;
  location: string | null;
  area: number | null;
  soil_type: string | null;
  irrigation_type: string | null;
  is_active?: boolean;
  created_at: string;
  zone_count?: number;
  device_count?: number;
  crops: Array<{
    id: number;
    crop_type: string;
    growth_stage: string | null;
    planting_date: string | null;
  }>;
};

export type FarmOverview = {
  farm: Farm;
  latest_reading: SensorReading | null;
  latest_prediction: Prediction | null;
  zone_names: string[];
  anomaly_count: number;
  open_irrigation: boolean;
  water_used_liters?: number | null;
  water_savings_liters?: number | null;
  water_savings_pct?: number | null;
  water_usage_note?: string | null;
};

export type TwinView = {
  farm: Farm;
  zones: Array<{
    id: number | null;
    name: string;
    soil_moisture: number | null;
    soil_temperature: number | null;
    air_temperature: number | null;
    air_humidity: number | null;
    ec: number | null;
    risk: string;
  }>;
  latest_reading: SensorReading | null;
  latest_prediction: Prediction | null;
  source_label: string | null;
  confidence: number | null;
  insight: string | null;
};

export type DataSource = {
  key: string;
  name: string;
  source_type: string;
  status: "active" | "pending" | "offline";
  last_update: string | null;
  record_count: number;
  trust_score: number | null;
  detail: string | null;
};

export type SensorReading = {
  id: number;
  farm_id: number;
  zone_id?: number | null;
  source_type:
    | "manual"
    | "simulation"
    | "test_dataset"
    | "lab_report"
    | "lab_manual"
    | "iot";
  timestamp: string;
  soil_moisture: number;
  soil_moisture_deep?: number | null;
  moisture_depth_cm?: number | null;
  moisture_deep_depth_cm?: number | null;
  soil_temperature: number | null;
  air_temperature: number | null;
  air_humidity: number | null;
  rainfall_probability: number | null;
  data_confidence: number | null;
  last_irrigation_hours_ago: number | null;
  ph?: number | null;
  ec?: number | null;
  is_validated?: boolean;
};

export type ManagementZone = {
  id: number;
  farm_id: number;
  name: string;
  notes: string | null;
  created_at: string;
};

export type LabParameter = {
  id?: number;
  parameter_code: string;
  value: number;
  unit: string;
  method?: string | null;
  extracted_auto?: boolean;
  confidence_pct?: number | null;
};

export type LabReport = {
  id: number;
  farm_id: number;
  zone_id: number | null;
  lab_name: string;
  report_number: string | null;
  analysis_date: string | null;
  sample_date: string | null;
  sample_depth_cm: string | null;
  sample_region: string | null;
  file_name: string | null;
  source_type: "lab_report" | "lab_manual";
  user_confirmed: boolean;
  notes: string | null;
  created_at: string;
  status?: string | null;
  extraction_confidence?: number | null;
  parameters: LabParameter[];
  critical_count?: number;
  ph?: number | null;
  ec?: number | null;
  om?: number | null;
};

export type LabSummary = {
  farm_id: number;
  total: number;
  pending: number;
  verified: number;
  missing: number;
  last_30_days: number;
  critical_findings: number;
};

export type LabInsight = {
  parameter_code: string;
  label: string;
  value: number;
  unit: string;
  status_label: string;
  tone: string;
  risk: string;
  message: string;
};

export type LabDetail = {
  report: LabReport;
  insights: LabInsight[];
  ai_summary: string;
  source_note: string;
};

export type Prediction = {
  id: number;
  farm_id: number;
  irrigation_needed: boolean;
  irrigation_duration: number | null;
  risk_level: "low" | "medium" | "high" | "critical";
  confidence_score: number;
  explanation: string;
  moisture_24h: number | null;
  moisture_48h: number | null;
  moisture_72h: number | null;
  created_at: string;
};

export type ScenarioType =
  | "irrigate_now"
  | "wait_12h"
  | "wait_24h"
  | "skip"
  | "reduce_duration"
  | "increase_duration";

export type ScenarioResult = {
  scenario: ScenarioType;
  label: string;
  estimated_moisture: number;
  estimated_water_liters: number | null;
  risk_level: Prediction["risk_level"];
  plant_stress: string;
  recommended: boolean;
  explanation: string;
};

export type ScenarioCompare = {
  farm_id: number;
  current_moisture: number;
  recommended_scenario: ScenarioType;
  results: ScenarioResult[];
};

export type CustomSimulateResult = {
  farm_id: number;
  name: string | null;
  current_moisture: number;
  estimated_moisture: number;
  estimated_water_liters: number;
  estimated_water_mm: number;
  estimated_cost_try: number;
  duration_minutes: number;
  risk_level: Prediction["risk_level"];
  plant_stress: string;
  forecast: Array<{
    day: number;
    current_path: number;
    scenario_path: number;
    critical_level: number;
  }>;
  explanation: string;
};

export type RecommendationItem = {
  id: string;
  prediction_id: number | null;
  category: "irrigation" | "climate" | "other";
  title: string;
  summary: string;
  priority: "high" | "medium" | "low";
  risk_level?: Prediction["risk_level"] | null;
  confidence_score?: number | null;
  irrigation_needed?: boolean | null;
  created_at?: string | null;
  automation_allowed: boolean;
};

export type RecommendationSummary = {
  farm_id: number;
  total: number;
  high: number;
  medium: number;
  low: number;
  items: RecommendationItem[];
};

export type RecommendationDetail = {
  prediction: Prediction;
  title: string;
  priority: "high" | "medium" | "low";
  automation_allowed: boolean;
  factors: string[];
  data_sources: string[];
  current_moisture: number | null;
  estimated_water_mm: number | null;
  can_apply: boolean;
  apply_block_reason: string | null;
};

export type FarmHub = {
  farm_id: number;
  farm_name: string;
  alerts: Array<{
    code: string;
    severity: string;
    title: string;
    message: string;
  }>;
  alert_counts: Record<string, number>;
  reports: Array<{
    key: string;
    title: string;
    description: string;
    available: boolean;
    record_count: number;
    metric_label?: string | null;
    metric_value?: string | null;
  }>;
  settings: Record<string, string | number | boolean | null>;
  note: string;
  water_used_liters?: number | null;
  water_savings_liters?: number | null;
  water_savings_pct?: number | null;
  water_usage_note?: string | null;
};

export type IrrigationEvent = {
  id: number;
  farm_id: number;
  start_time: string;
  end_time: string | null;
  duration: number | null;
  water_amount: number | null;
  status: "pending" | "running" | "completed" | "stopped";
  valve_status: string;
};

export type IrrigationStartResult = {
  event: IrrigationEvent;
  updated_moisture: number;
  prediction: Prediction;
  message: string;
};

export type Anomaly = {
  code: string;
  severity: string;
  title: string;
  message: string;
};

export type AnomalyReport = {
  farm_id: number;
  has_anomalies: boolean;
  count: number;
  anomalies: Anomaly[];
};

export type Device = {
  id: number;
  farm_id: number;
  device_name: string;
  device_type: string;
  connection_status: string;
  last_data_time: string | null;
  serial_number?: string | null;
  zone_id?: number | null;
  region_name?: string | null;
  depth_cm?: number | null;
  connection_type?: string | null;
  battery_percent?: number | null;
  signal_dbm?: number | null;
  firmware_version?: string | null;
  installed_at?: string | null;
  last_calibration_at?: string | null;
  calibration_offset?: number | null;
  sampling_minutes?: number | null;
  notes?: string | null;
  last_moisture?: number | null;
  calibration_due?: boolean;
  source_label?: string;
};

export type DeviceSummary = {
  farm_id: number;
  total: number;
  online: number;
  warning: number;
  offline: number;
  calibration_pending: number;
  online_percent: number;
};

export type DeviceDetail = {
  device: Device;
  recent_readings: SensorReading[];
  events: string[];
};

export type DeviceCalibrateResult = {
  device_id: number;
  raw_value: number;
  reference_value: number;
  deviation: number;
  status: string;
  calibration_offset: number;
  last_calibration_at: string;
  message: string;
};

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("agritwin_token");
}

export function setSession(token: string, user: User) {
  localStorage.setItem("agritwin_token", token);
  localStorage.setItem("agritwin_user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("agritwin_token");
  localStorage.removeItem("agritwin_user");
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("agritwin_user");
  return raw ? (JSON.parse(raw) as User) : null;
}

export function setStoredUser(user: User) {
  if (typeof window === "undefined") return;
  localStorage.setItem("agritwin_user", JSON.stringify(user));
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (auth) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  const text = await res.text();
  if (res.status === 204) {
    return null as T;
  }
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }
  if (!res.ok) {
    let detail = "İstek başarısız.";
    if (typeof data === "object" && data && "detail" in data) {
      const d = (data as { detail: unknown }).detail;
      if (typeof d === "string") detail = d;
      else if (Array.isArray(d)) {
        detail = d
          .map((item) =>
            typeof item === "object" && item && "msg" in item
              ? String((item as { msg: unknown }).msg)
              : String(item),
          )
          .join(" ");
      } else if (d != null) detail = String(d);
    }
    throw new Error(detail);
  }
  return data as T;
}

export const api = {
  register: (body: {
    name: string;
    email: string;
    password: string;
    phone?: string;
    role?: string;
  }) =>
    request<RegisterPending>(
      "/auth/register",
      { method: "POST", body: JSON.stringify(body) },
      false,
    ),
  verify: (body: { email: string; code: string }) =>
    request<{ access_token: string; user: User }>(
      "/auth/verify",
      { method: "POST", body: JSON.stringify(body) },
      false,
    ),
  resendCode: (body: { email: string }) =>
    request<MessageOut>(
      "/auth/resend-code",
      { method: "POST", body: JSON.stringify(body) },
      false,
    ),
  updateRole: (role: "farmer" | "agronomist" | "cooperative" | "consultant") =>
    request<User>("/auth/me/role", {
      method: "PATCH",
      body: JSON.stringify({ role }),
    }),
  updateMe: (body: {
    name?: string;
    phone?: string | null;
    current_password?: string;
    new_password?: string;
  }) =>
    request<User>("/auth/me", {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  me: () => request<User>("/auth/me"),
  forgotPassword: (body: { email: string }) =>
    request<MessageOut>(
      "/auth/forgot-password",
      { method: "POST", body: JSON.stringify(body) },
      false,
    ),
  resetPassword: (body: {
    email: string;
    code: string;
    new_password: string;
  }) =>
    request<MessageOut>(
      "/auth/reset-password",
      { method: "POST", body: JSON.stringify(body) },
      false,
    ),
  login: (body: { email: string; password: string }) =>
    request<{ access_token: string; user: User }>(
      "/auth/login",
      { method: "POST", body: JSON.stringify(body) },
      false,
    ),
  listFarms: (includeInactive = false) =>
    request<Farm[]>(
      `/farms${includeInactive ? "?include_inactive=true" : ""}`,
    ),
  createFarm: (body: Record<string, unknown>) =>
    request<Farm>("/farms", { method: "POST", body: JSON.stringify(body) }),
  getFarm: (id: number) => request<Farm>(`/farms/${id}`),
  updateFarm: (id: number, body: Record<string, unknown>) =>
    request<Farm>(`/farms/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  deleteFarm: (id: number) =>
    request<null>(`/farms/${id}`, { method: "DELETE" }),
  farmOverview: (id: number) =>
    request<FarmOverview>(`/farms/${id}/overview`),
  farmTwin: (id: number) => request<TwinView>(`/farms/${id}/twin`),
  dataSources: (id: number) =>
    request<DataSource[]>(`/farms/${id}/data-sources`),
  createReading: (farmId: number, body: Record<string, unknown>) =>
    request<SensorReading>(`/sensor-readings/${farmId}`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listReadings: (farmId: number, limit = 50) =>
    request<SensorReading[]>(`/sensor-readings/${farmId}?limit=${limit}`),
  listDatasets: () =>
    request<Array<{ id: string; name: string; description?: string | null }>>(
      "/datasets",
    ),
  loadDataset: (
    farmId: number,
    scenario = "drought_risk",
    zoneId?: number | null,
  ) =>
    request<SensorReading>("/datasets/load", {
      method: "POST",
      body: JSON.stringify({
        farm_id: farmId,
        scenario,
        zone_id: zoneId ?? null,
      }),
    }),
  predict: (farmId: number) =>
    request<Prediction>(`/predict/irrigation?farm_id=${farmId}`, {
      method: "POST",
    }),
  listPredictions: (farmId: number) =>
    request<Prediction[]>(`/predictions/${farmId}`),
  iotSimulate: (farmId: number, scenario = "drought_risk") =>
    request<SensorReading>("/iot/simulate", {
      method: "POST",
      body: JSON.stringify({ farm_id: farmId, scenario }),
    }),
  compareScenarios: (
    farmId: number,
    scenarios: ScenarioType[] = ["irrigate_now", "wait_24h"],
    durationMinutes?: number,
  ) =>
    request<ScenarioCompare>("/simulate/scenario", {
      method: "POST",
      body: JSON.stringify({
        farm_id: farmId,
        scenarios,
        duration_minutes: durationMinutes ?? null,
      }),
    }),
  customSimulate: (body: {
    farm_id: number;
    duration_minutes: number;
    water_amount_liters?: number;
    target_moisture?: number;
    name?: string;
  }) =>
    request<CustomSimulateResult>("/simulate/custom", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  startIrrigation: (
    farmId: number,
    durationMinutes?: number,
    virtualSession = false,
  ) =>
    request<IrrigationStartResult>("/irrigation/start", {
      method: "POST",
      body: JSON.stringify({
        farm_id: farmId,
        user_approved: true,
        duration_minutes: durationMinutes ?? null,
        virtual_session: virtualSession,
      }),
    }),
  stopIrrigation: (farmId: number, eventId?: number) =>
    request<IrrigationEvent>("/irrigation/stop", {
      method: "POST",
      body: JSON.stringify({
        farm_id: farmId,
        event_id: eventId ?? null,
      }),
    }),
  irrigationHistory: (farmId: number) =>
    request<IrrigationEvent[]>(`/irrigation/history/${farmId}`),
  irrigationStatus: (farmId: number) =>
    request<{
      farm_id: number;
      valve_status: string;
      pump_status?: string;
      running: IrrigationEvent | null;
      remaining_seconds?: number | null;
      planned_end?: string | null;
      current_moisture: number | null;
      confidence_score: number;
      automation_allowed: boolean;
      message: string;
    }>(`/irrigation/status/${farmId}`),
  listRecommendations: (
    farmId: number,
    params?: { category?: string; priority?: string },
  ) => {
    const qs = new URLSearchParams();
    if (params?.category) qs.set("category", params.category);
    if (params?.priority) qs.set("priority", params.priority);
    const suffix = qs.toString() ? `?${qs}` : "";
    return request<RecommendationSummary>(
      `/recommendations/${farmId}${suffix}`,
    );
  },
  getRecommendationDetail: (predictionId: number) =>
    request<RecommendationDetail>(
      `/recommendations/detail/${predictionId}`,
    ),
  farmHub: (farmId: number) => request<FarmHub>(`/hub/${farmId}`),
  getAnomalies: (farmId: number) =>
    request<AnomalyReport>(`/anomalies/${farmId}`),
  createZone: (body: { farm_id: number; name: string; notes?: string }) =>
    request<ManagementZone>("/zones", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listZones: (farmId: number) =>
    request<ManagementZone[]>(`/zones/${farmId}`),
  getZone: (zoneId: number) =>
    request<ManagementZone>(`/zones/detail/${zoneId}`),
  updateZone: (
    zoneId: number,
    body: { name?: string; notes?: string | null },
  ) =>
    request<ManagementZone>(`/zones/detail/${zoneId}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  deleteZone: (zoneId: number) =>
    request<null>(`/zones/detail/${zoneId}`, { method: "DELETE" }),
  createLabReport: (body: Record<string, unknown>) =>
    request<LabReport>("/lab-reports", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listLabReports: (farmId: number, params?: { status?: string; q?: string }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.q) qs.set("q", params.q);
    const suffix = qs.toString() ? `?${qs}` : "";
    return request<LabReport[]>(`/lab-reports/${farmId}${suffix}`);
  },
  labSummary: (farmId: number) =>
    request<LabSummary>(`/lab-reports/${farmId}/summary`),
  getLabDetail: (reportId: number) =>
    request<LabDetail>(`/lab-reports/detail/${reportId}`),
  updateLabReport: (reportId: number, body: Record<string, unknown>) =>
    request<LabReport>(`/lab-reports/detail/${reportId}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  deleteLabReport: (reportId: number) =>
    request<null>(`/lab-reports/detail/${reportId}`, { method: "DELETE" }),
  confirmLabReport: (
    reportId: number,
    body: { confirmed: boolean; parameters?: LabParameter[] },
  ) =>
    request<LabReport>(`/lab-reports/${reportId}/confirm`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  labExtractDemo: () =>
    request<{
      parameters: LabParameter[];
      extraction_confidence: number;
      message: string;
    }>("/lab-reports/extract-demo"),
  uploadLabFile: async (farmId: number, file: File) => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("agritwin_token")
        : null;
    const fd = new FormData();
    fd.append("farm_id", String(farmId));
    fd.append("file", file);
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/lab-reports/upload`,
      {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: fd,
      },
    );
    const data = await res.json();
    if (!res.ok) {
      throw new Error(
        typeof data?.detail === "string" ? data.detail : "Yükleme başarısız",
      );
    }
    return data as {
      file_name: string;
      original_name: string;
      size_bytes: number;
      message: string;
    };
  },
  listDevices: (
    farmId: number,
    params?: { status?: string; device_type?: string; q?: string },
  ) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.device_type) qs.set("device_type", params.device_type);
    if (params?.q) qs.set("q", params.q);
    const suffix = qs.toString() ? `?${qs}` : "";
    return request<Device[]>(`/devices/${farmId}${suffix}`);
  },
  deviceSummary: (farmId: number) =>
    request<DeviceSummary>(`/devices/${farmId}/summary`),
  createDevice: (body: Record<string, unknown>) =>
    request<Device>("/devices", { method: "POST", body: JSON.stringify(body) }),
  getDeviceDetail: (deviceId: number) =>
    request<DeviceDetail>(`/devices/detail/${deviceId}`),
  updateDevice: (deviceId: number, body: Record<string, unknown>) =>
    request<Device>(`/devices/detail/${deviceId}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  deleteDevice: (deviceId: number) =>
    request<null>(`/devices/detail/${deviceId}`, { method: "DELETE" }),
  calibrateDevice: (
    deviceId: number,
    body: { reference_value: number; raw_value?: number },
  ) =>
    request<DeviceCalibrateResult>(`/devices/detail/${deviceId}/calibrate`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  testDevice: (deviceId: number) =>
    request<{
      device_id: number;
      connection_status: string;
      message: string;
      last_data_time: string | null;
      signal_dbm?: number | null;
      battery_percent?: number | null;
    }>("/devices/test-connection", {
      method: "POST",
      body: JSON.stringify({ device_id: deviceId }),
    }),
  iotSimulateForDevice: (
    farmId: number,
    deviceId: number,
    scenario = "drought_risk",
  ) =>
    request<SensorReading>("/iot/simulate", {
      method: "POST",
      body: JSON.stringify({
        farm_id: farmId,
        scenario,
        device_id: deviceId,
      }),
    }),
  adminBootstrap: () =>
    request<User>("/admin/bootstrap", { method: "POST" }),
  adminOverview: () => request<AdminOverview>("/admin/overview"),
  adminUsers: (params?: { status?: string; role?: string; q?: string }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.role) qs.set("role", params.role);
    if (params?.q) qs.set("q", params.q);
    const s = qs.toString() ? `?${qs}` : "";
    return request<AdminUser[]>(`/admin/users${s}`);
  },
  adminUpdateUser: (id: number, body: Record<string, unknown>) =>
    request<AdminUser>(`/admin/users/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  adminFarms: (params?: { status?: string; q?: string }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.q) qs.set("q", params.q);
    const s = qs.toString() ? `?${qs}` : "";
    return request<AdminFarm[]>(`/admin/farms${s}`);
  },
  adminUpdateFarm: (id: number, body: Record<string, unknown>) =>
    request<AdminFarm>(`/admin/farms/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  adminDevices: (params?: { status?: string; q?: string }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.q) qs.set("q", params.q);
    const s = qs.toString() ? `?${qs}` : "";
    return request<AdminDevice[]>(`/admin/devices${s}`);
  },
  adminUpdateDevice: (id: number, body: Record<string, unknown>) =>
    request<AdminDevice>(`/admin/devices/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  adminBilling: () => request<AdminBilling>("/admin/billing"),
  adminTickets: (status?: string) => {
    const s = status ? `?status=${status}` : "";
    return request<SupportTicket[]>(`/admin/tickets${s}`);
  },
  createTicket: (body: {
    subject: string;
    description?: string;
    priority?: string;
    farm_id?: number;
  }) =>
    request<SupportTicket>("/admin/tickets", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  adminUpdateTicket: (id: number, body: Record<string, unknown>) =>
    request<SupportTicket>(`/admin/tickets/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  adminDeleteTicket: (id: number) =>
    request<null>(`/admin/tickets/${id}`, { method: "DELETE" }),
  adminAnalytics: (days = 30) =>
    request<AdminAnalytics>(`/admin/analytics?days=${days}`),
  adminSettings: () => request<AdminSettings>("/admin/settings"),
  adminUpdateSettings: (settings: Record<string, string>) =>
    request<AdminSettings>("/admin/settings", {
      method: "PUT",
      body: JSON.stringify({ settings }),
    }),
};
