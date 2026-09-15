/**
 * Nexus API Client
 * Enforces typed API requests, authentication header injection, and standardized error extraction.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, code: string = "UNKNOWN_ERROR", status: number = 500) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;

  const headers: HeadersInit = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    credentials: "include",
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData: Record<string, unknown> = {};
    try {
      errorData = (await response.json()) as Record<string, unknown>;
    } catch {
      // Non-JSON response
    }
    const errorObj =
      typeof errorData?.error === "object" && errorData.error !== null
        ? (errorData.error as Record<string, unknown>)
        : null;
    const message =
      (typeof errorObj?.message === "string" ? errorObj.message : null) ||
      (typeof errorData?.detail === "string" ? errorData.detail : null) ||
      response.statusText ||
      "Request failed";
    const code =
      (typeof errorObj?.code === "string" ? errorObj.code : null) ||
      `HTTP_${response.status}`;
    throw new ApiError(message, code, response.status);
  }

  // Support 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
