//import { motion } from 'motion/react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';

interface MainPageProps {
  onWordSelect: (word: string) => void;
}

const words = [
  { title: '인공지능', emoji: '🤖', color: 'bg-blue-100 text-blue-800' },
  { title: '우주과학', emoji: '🚀', color: 'bg-purple-100 text-purple-800' },
  { title: '생명과학', emoji: '🧬', color: 'bg-green-100 text-green-800' },
  { title: '양자역학', emoji: '⚛️', color: 'bg-orange-100 text-orange-800' },
  { title: '기후변화', emoji: '🌍', color: 'bg-teal-100 text-teal-800' }
];

export function MainPage({ onWordSelect }: MainPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex flex-col items-center justify-center p-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <h1 className="text-4xl mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
          지식 탐험
        </h1>
        <p className="text-lg text-gray-600">관심 있는 주제를 선택하여 마인드맵을 탐험해보세요</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 max-w-6xl">
        {words.map((word, index) => (
          <motion.div
            key={word.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.05, y: -5 }}
            whileTap={{ scale: 0.95 }}
          >
            <Card 
              className="cursor-pointer bg-white/70 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300"
              onClick={() => onWordSelect(word.title)}
            >
              <CardContent className="p-8 text-center">
                <div className="text-4xl mb-4">{word.emoji}</div>
                <div className={`inline-block px-4 py-2 rounded-full ${word.color} transition-all duration-300`}>
                  <span className="font-medium">{word.title}</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5 }}
        className="mt-12 text-gray-500 text-center max-w-md"
      >
        각 주제를 클릭하면 관련된 개념들이 연결된 마인드맵을 볼 수 있습니다
      </motion.p>
    </div>
  );
}