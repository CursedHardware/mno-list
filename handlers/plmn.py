__all__ = ["PLMN"]


class PLMN(bytes):
    @classmethod
    def from_mccmnc_tuple(cls, mccmnc_tuple: str) -> "PLMN":
        return cls.from_tuple(mccmnc_tuple[:3], mccmnc_tuple[3:])

    @staticmethod
    def from_tuple(mcc: str, mnc: str) -> "PLMN":
        mcc = list(map(int, mcc))
        mnc = list(map(int, mnc))
        if len(mnc) == 2:
            mnc.append(0xf)
        return PLMN([
            mcc[1] << 4 | mcc[0],
            mnc[2] << 4 | mcc[2],
            mnc[1] << 4 | mnc[0],
        ])

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
