import type { Tool } from 'ai';

export interface FidemAnswer {
  schema?: string;
  domain?: string;
  checked_at?: string;
  decision?: 'verified' | 'domain_proven' | 'fictitious_demo' | 'revoked' | 'expired' | 'invalid_file' | 'in_review' | 'not_verified' | 'no_data';
  identity_verified?: boolean;
  level?: 'merchant_verified' | 'public_lookup';
  lookup_status?: 'complete' | 'in_progress' | 'busy';
  retry_after_seconds?: number;
  mvf_file?: Record<string, unknown>;
  company?: Record<string, unknown>;
  error?: string;
  [key: string]: unknown;
}

export interface FidemOptions {
  /** fetch to use (defaults to globalThis.fetch). */
  fetch?: typeof globalThis.fetch;
  /** How long to keep asking while the first lookup of a domain is still running. Default 45. */
  maxWaitSeconds?: number;
  signal?: AbortSignal;
}

export function fidemCheck(domain: string, options?: FidemOptions): Promise<FidemAnswer>;
export function isVerified(answer: FidemAnswer | null | undefined): boolean;
export function checkShop(options?: Omit<FidemOptions, 'signal'>): Tool<{ domain: string }, FidemAnswer>;
export default checkShop;
