export type Produce = {
  id: string;
  name: string;
  local: string;
  farmer: string;
  village: string;
  price: number;
  unit: string;
  mandiPrice: number;
  stock: number;
  harvested: string;
  category: "Vegetables" | "Fruits" | "Grains" | "Dairy";
  emoji: string;
};

export const produce: Produce[] = [
  {
    id: "onion-nashik",
    name: "Red Onion",
    local: "प्याज",
    farmer: "Ramesh Patil",
    village: "Nashik, MH",
    price: 28,
    unit: "kg",
    mandiPrice: 41,
    stock: 320,
    harvested: "2 days ago",
    category: "Vegetables",
    emoji: "🧅",
  },
  {
    id: "tomato-pune",
    name: "Vine Tomato",
    local: "टमाटर",
    farmer: "Sunita Jadhav",
    village: "Junnar, MH",
    price: 34,
    unit: "kg",
    mandiPrice: 52,
    stock: 140,
    harvested: "Today",
    category: "Vegetables",
    emoji: "🍅",
  },
  {
    id: "wheat-indore",
    name: "Sharbati Wheat",
    local: "गेहूं",
    farmer: "Mohan Verma",
    village: "Indore, MP",
    price: 39,
    unit: "kg",
    mandiPrice: 55,
    stock: 900,
    harvested: "1 week ago",
    category: "Grains",
    emoji: "🌾",
  },
  {
    id: "alphonso-ratnagiri",
    name: "Alphonso Mango",
    local: "हापूस",
    farmer: "Kiran Sawant",
    village: "Ratnagiri, MH",
    price: 640,
    unit: "dozen",
    mandiPrice: 890,
    stock: 48,
    harvested: "Today",
    category: "Fruits",
    emoji: "🥭",
  },
  {
    id: "okra-anand",
    name: "Tender Okra",
    local: "भिंडी",
    farmer: "Bhavna Desai",
    village: "Anand, GJ",
    price: 42,
    unit: "kg",
    mandiPrice: 60,
    stock: 85,
    harvested: "Yesterday",
    category: "Vegetables",
    emoji: "🌿",
  },
  {
    id: "milk-kolhapur",
    name: "A2 Cow Milk",
    local: "दूध",
    farmer: "Dattatray Kale",
    village: "Kolhapur, MH",
    price: 62,
    unit: "litre",
    mandiPrice: 78,
    stock: 210,
    harvested: "This morning",
    category: "Dairy",
    emoji: "🥛",
  },
  {
    id: "potato-agra",
    name: "Chipsona Potato",
    local: "आलू",
    farmer: "Arun Singh",
    village: "Agra, UP",
    price: 22,
    unit: "kg",
    mandiPrice: 33,
    stock: 640,
    harvested: "3 days ago",
    category: "Vegetables",
    emoji: "🥔",
  },
  {
    id: "banana-jalgaon",
    name: "Grand Naine Banana",
    local: "કેळी",
    farmer: "Pooja Mahajan",
    village: "Jalgaon, MH",
    price: 46,
    unit: "dozen",
    mandiPrice: 65,
    stock: 130,
    harvested: "Yesterday",
    category: "Fruits",
    emoji: "🍌",
  },
];

export const categories = ["All", "Vegetables", "Fruits", "Grains", "Dairy"] as const;

export type FarmerOrder = {
  id: string;
  buyer: string;
  item: string;
  qty: string;
  amount: number;
  status: "Packing" | "In transit" | "Delivered";
  eta: string;
};

export const farmerOrders: FarmerOrder[] = [
  { id: "KS-2481", buyer: "Meera Iyer", item: "Vine Tomato", qty: "12 kg", amount: 408, status: "In transit", eta: "Today, 6:30 pm" },
  { id: "KS-2480", buyer: "Aditya Rao", item: "Red Onion", qty: "40 kg", amount: 1120, status: "Packing", eta: "Tomorrow, 9 am" },
  { id: "KS-2478", buyer: "Fresh Basket Co-op", item: "Tender Okra", qty: "25 kg", amount: 1050, status: "Delivered", eta: "Delivered" },
  { id: "KS-2475", buyer: "Nikhil Shah", item: "A2 Cow Milk", qty: "20 L", amount: 1240, status: "Delivered", eta: "Delivered" },
];

export const earningsByWeek = [
  { week: "W1", direct: 9200, mandi: 6100 },
  { week: "W2", direct: 11400, mandi: 6400 },
  { week: "W3", direct: 10250, mandi: 5800 },
  { week: "W4", direct: 14800, mandi: 6900 },
  { week: "W5", direct: 17300, mandi: 7100 },
  { week: "W6", direct: 19600, mandi: 7000 },
];
