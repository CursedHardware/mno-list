__all__ = ["PLMN"]


class PLMN(bytes):
    @staticmethod
    def from_mccmnc_tuple(mccmnc_tuple: str) -> "PLMN":
        mccmnc_tuple = bytearray(_ - 0x30 for _ in mccmnc_tuple.encode("ascii"))
        mccmnc_tuple.append(0xf)
        return PLMN([
            mccmnc_tuple[1] << 4 | mccmnc_tuple[0],
            mccmnc_tuple[5] << 4 | mccmnc_tuple[2],
            mccmnc_tuple[4] << 4 | mccmnc_tuple[3],
        ])

    @classmethod
    def from_tuple(cls, mcc: str, mnc: str) -> "PLMN":
        return cls.from_mccmnc_tuple(mcc + mnc)

    @property
    def mcc(self) -> str:
        mcc = [(self[0] & 0x0F), (self[0] & 0xF0) >> 4, (self[1] & 0x0F)]
        return bytes(_ + 0x30 for _ in mcc if _ != 0xf).decode("ascii")

    @property
    def mnc(self) -> str:
        mnc = [(self[2] & 0x0F), (self[2] & 0xF0) >> 4, (self[1] & 0xF0) >> 4]
        return bytes(_ + 0x30 for _ in mnc if _ != 0xf).decode("ascii")

    @property
    def mccmnc(self) -> str:
        return self.mcc + self.mnc

    def __repr__(self):
        return self.mccmnc
