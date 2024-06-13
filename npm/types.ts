export interface Carrier {
  readonly mcc: string;
  readonly mnc: string;
  readonly iso?: string;
  readonly country: string;
  readonly country_code?: string;
  readonly network: string;
}
