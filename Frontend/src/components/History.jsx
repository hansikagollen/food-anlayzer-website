function History({ history }) {
  return (
    <div className="historyBox">
      <h3>📜 History</h3>
      <ul>
        {history.map((item, index) => (
          <li key={index}>
            {item.food_name} - {item.freshness_class}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default History;