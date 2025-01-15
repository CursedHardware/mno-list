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
        /** A unique canonical number designated to a carrier. */
        readonly canonical_id: number;
        /** A unique canonical number to represent its parent carrier. */
        readonly parent_canonical_id: number;
        /** A user-friendly carrier name (not localized). */
        readonly carrier_name: string | null;
        /** Carrier attributes to match a carrier. */
        readonly carrier_attribute: readonly CarrierAttribute[];
    }

    export interface CarrierAttribute {
        /** The MCC and MNC that map to this carrier. */
        readonly mccmnc_tuple?: readonly string[];
        /** Prefix of IMSI (International Mobile Subscriber Identity) in decimal format. */
        readonly imsi_prefix_xpattern?: readonly string[];
        /** The Service Provider Name. Read from subscription EF_SPN. */
        readonly spn?: readonly string[];
        /** PLMN network name. Read from subscription EF_PNN. */
        readonly plmn?: readonly string[];
        /** Group Identifier Level 1 for a GSM phone. Read from subscription EF_GID1. */
        readonly gid1?: readonly string[];
        /** Group Identifier Level 2 for a GSM phone. Read from subscription EF_GID2. */
        readonly gid2?: readonly string[];
        /** The Access Point Name */
        readonly preferred_apn?: readonly string[];
        /** Prefix of Integrated Circuit Card Identifier. Read from subscription EF_ICCID. */
        readonly iccid_prefix?: readonly string[];
        /** Carrier Privilege Access Rule in hex string. */
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