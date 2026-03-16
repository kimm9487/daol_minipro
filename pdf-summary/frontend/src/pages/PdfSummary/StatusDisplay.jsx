import React from "react";

const StatusDisplay = ({ status }) => {
  if (!status.msg) return null;

  return <div className={`status ${status.type}`}>{status.msg}</div>;
};

export default StatusDisplay;
