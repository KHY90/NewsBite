import React from "react";

interface SpinnerProps {
  size?: "sm" | "md" | "lg" | "xl";
  color?: string;
  className?: string;
}

const Spinner: React.FC<SpinnerProps> = ({
  size = "md",
  color = "border-brand-primary",
  className = "",
}) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-12 w-12",
    xl: "h-24 w-24",
  };

  return (
    <div
      className={`animate-spin rounded-full border-b-2 ${sizeClasses[size]} ${color} ${className}`}
    />
  );
};

export default Spinner;
