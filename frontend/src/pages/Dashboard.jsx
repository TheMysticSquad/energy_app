import { useEffect, useState } from "react";
import { getFilters, getKpis } from "../api";
import ChartCard from "../components/ChartCard";

export default function Dashboard() {
  const [filters, setFilters] = useState({});
  const [kpis, setKpis] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      const employeeId = 1; // Example employee ID
      const { data: filterData } = await getFilters(employeeId);
      setFilters(filterData);

      const sectionId = filterData.sections?.[0]?.SectionID;
      const year = new Date().getFullYear();
      const month = new Date().getMonth() + 1;

      const { data: kpiData } = await getKpis(sectionId, year, month);
      setKpis(kpiData);
      setLoading(false);
    };
    loadData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl mb-4">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(kpis).map(([key, value]) => (
          <ChartCard key={key} title={key} data={value} />
        ))}
      </div>
    </div>
  );
}
