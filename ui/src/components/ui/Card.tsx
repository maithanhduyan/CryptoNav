import React from 'react';

interface CardProps {
  title: string;
  content: string | number;
}

const Card: React.FC<CardProps> = ({ title, content }) => {
  return (
    <div className="bg-white shadow-md rounded-lg p-4">
      <h5 className="text-lg font-semibold text-gray-900">{title}</h5>
      <p className="text-gray-700">{content}</p>
    </div>
  );
};

export default Card;