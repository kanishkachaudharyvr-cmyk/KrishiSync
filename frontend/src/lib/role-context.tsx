import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type Role = "customer" | "farmer";

export type CustomerSettings = {
  name: string;
  phone: string;
  address: string;
  deliverySlot: string;
  organicOnly: boolean;
};

export type FarmerSettings = {
  name: string;
  village: string;
  farmSize: string;
  payoutUpi: string;
  autoAcceptOrders: boolean;
};

type Ctx = {
  role: Role;
  setRole: (r: Role) => void;
  customer: CustomerSettings;
  setCustomer: (c: Partial<CustomerSettings>) => void;
  farmer: FarmerSettings;
  setFarmer: (f: Partial<FarmerSettings>) => void;
};

const defaultCustomer: CustomerSettings = {
  name: "Meera Iyer",
  phone: "+91 98765 43210",
  address: "Koregaon Park, Pune",
  deliverySlot: "Morning (7–10 am)",
  organicOnly: false,
};

const defaultFarmer: FarmerSettings = {
  name: "Ramesh Patil",
  village: "Nashik, MH",
  farmSize: "4 acres",
  payoutUpi: "ramesh@upi",
  autoAcceptOrders: true,
};

const RoleContext = createContext<Ctx | null>(null);
const KEY = "krishisync.profile";

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRoleState] = useState<Role>("customer");
  const [customer, setCustomerState] = useState<CustomerSettings>(defaultCustomer);
  const [farmer, setFarmerState] = useState<FarmerSettings>(defaultFarmer);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw) as Partial<{
        role: Role;
        customer: CustomerSettings;
        farmer: FarmerSettings;
      }>;
      if (parsed.role === "farmer" || parsed.role === "customer") setRoleState(parsed.role);
      if (parsed.customer) setCustomerState({ ...defaultCustomer, ...parsed.customer });
      if (parsed.farmer) setFarmerState({ ...defaultFarmer, ...parsed.farmer });
    } catch {
      /* ignore corrupt storage */
    }
  }, []);

  const value = useMemo<Ctx>(() => {
    const persist = (next: { role?: Role; customer?: CustomerSettings; farmer?: FarmerSettings }) => {
      window.localStorage.setItem(
        KEY,
        JSON.stringify({ role, customer, farmer, ...next }),
      );
    };
    return {
      role,
      customer,
      farmer,
      setRole: (r) => {
        setRoleState(r);
        persist({ role: r });
      },
      setCustomer: (patch) => {
        const next = { ...customer, ...patch };
        setCustomerState(next);
        persist({ customer: next });
      },
      setFarmer: (patch) => {
        const next = { ...farmer, ...patch };
        setFarmerState(next);
        persist({ farmer: next });
      },
    };
  }, [role, customer, farmer]);

  return <RoleContext.Provider value={value}>{children}</RoleContext.Provider>;
}

export function useRole() {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error("useRole must be used inside RoleProvider");
  return ctx;
}
