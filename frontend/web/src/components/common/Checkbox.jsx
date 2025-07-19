
import React from 'react';

const Checkbox = ({ id, label }) => {
  return (
    <div className="flex items-center">
      <input
        id={id}
        type="checkbox"
        className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
      />
      <label htmlFor={id} className="ml-2 block text-sm text-gray-600">
        {label}
      </label>
    </div>
  );
};

export default Checkbox;
