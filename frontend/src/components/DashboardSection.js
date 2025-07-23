import React from 'react';

const DashboardSection = ({ 
  title, 
  icon, 
  description, 
  children, 
  className = "", 
  headerColor = "text-white",
  borderColor = "border-gray-600",
  collapsible = false,
  defaultExpanded = true 
}) => {
  const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);

  return (
    <div className={`dashboard-section ${className}`}>
      {/* Section Header */}
      <div className={`section-header ${borderColor} border-b pb-3 mb-4`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className={`text-2xl ${headerColor}`}>{icon}</span>
            <div>
              <h2 className={`text-xl font-bold ${headerColor}`}>{title}</h2>
              {description && (
                <p className="text-sm text-gray-400 mt-1">{description}</p>
              )}
            </div>
          </div>
          
          {collapsible && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-gray-400 hover:text-white transition-colors p-2"
            >
              <svg 
                className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Section Content */}
      {(!collapsible || isExpanded) && (
        <div className="section-content">
          {children}
        </div>
      )}
    </div>
  );
};

export default DashboardSection;