import type React from "react"
import { useState } from "react"
import { X } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface FeedbackModalProps {
  isOpen: boolean
  onClose: () => void
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ isOpen, onClose }) => {
  const [category, setCategory] = useState<string>("")
  const [feedback, setFeedback] = useState<string>("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!category) {
      alert("카테고리를 선택해주세요.")
      return
    }
    // TODO: Implement feedback submission logic
    console.log({ category, feedback })
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">피드백</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block mb-2 font-medium">카테고리</label>
            <Select onValueChange={setCategory} value={category}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="카테고리를 선택해주세요" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ui">UI/UX</SelectItem>
                <SelectItem value="content">콘텐츠</SelectItem>
                <SelectItem value="feature">기능</SelectItem>
                <SelectItem value="bug">버그</SelectItem>
                <SelectItem value="other">기타</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="mb-4">
            <label htmlFor="feedback" className="block mb-2">
              피드백 내용
            </label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="w-full p-2 border rounded"
              rows={4}
            ></textarea>
          </div>
          <button type="submit" className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">
            제출
          </button>
        </form>
      </div>
    </div>
  )
}

export default FeedbackModal

