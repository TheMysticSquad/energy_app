import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function ChartCard({ title, data }) {
  const labels = Object.keys(data || {});
  const values = Object.values(data || {});

  return (
    <div className="bg-white p-4 shadow rounded">
      <h2 className="text-lg mb-2">{title}</h2>
      <Bar
        data={{
          labels,
          datasets: [
            {
              label: title,
              data: values,
              backgroundColor: "rgba(54, 162, 235, 0.5)",
            },
          ],
        }}
      />
    </div>
  );
}
