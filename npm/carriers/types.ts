/**
 * data source from mcc-mnc.com and mcc-mnc.net
 *
 * @see https://mcc-mnc.com
 * @see https://mcc-mnc.net
 **/
export namespace unified {
    export interface PLMNByCountry {
        readonly [iso_code: string]: readonly string[];
    }

    export interface Carrier {
        readonly brand: string | null;
        readonly operator: string | null;
        readonly mccmnc_tuple: PLMNByCountry;
    }
}

/**
 * data source from google
 *
 * @see https://source.android.com/docs/core/connect/carrierid
 **/
export namespace carrierId {
    export interface CarrierId {
        readonly canonical_id: number;
        readonly parent_canonical_id: number;
        readonly carrier_name: string | null;
        readonly carrier_attribute: readonly CarrierAttribute[];
    }

    export interface CarrierAttribute {
        readonly mccmnc_tuple?: readonly string[];
        readonly imsi_prefix_xpattern?: readonly string[];
        readonly spn?: readonly string[];
        readonly plmn?: readonly string[];
        readonly gid1?: readonly string[];
        readonly gid2?: readonly string[];
        readonly preferred_apn?: readonly string[];
        readonly iccid_prefix?: readonly string[];
        readonly privilege_access_rule?: readonly string[];
    }

    export interface MCCEntry {
        readonly mcc: string;
        readonly iso: string;
        readonly smallestDigitsMCC: number;
    }
}

export namespace carrierConfig {
    export interface Entry {
        readonly carrier_id: number;
        readonly carrier_config: CarrierConfig | readonly CarrierConfig[];
    }

    export type CarrierConfig = {
        readonly [name: string]: boolean | string | string[] | number | number[];
    };
}