import { useState } from 'react'
import DBPage from './pages/DBPage'
import AnalysisPage from './pages/AnalysisPage'
import RecommendPage from './pages/RecommendPage'
import ReportPage from './pages/ReportPage'

const TABS = [
  { id: 'db',       label: 'DB 현황' },
  { id: 'analysis', label: '통계 분석' },
  { id: 'recommend',label: '번호 추천' },
  { id: 'report',   label: '전략 리포트' },
]

export default function App() {
  const [tab, setTab] = useState('db')

  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '20px', color: '#60a5fa' }}>
        🎱 Mangbing
      </h1>

      <nav style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            style={{
              padding: '8px 18px',
              borderRadius: '6px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              background: tab === t.id ? '#3b82f6' : '#1e293b',
              color: tab === t.id ? '#fff' : '#94a3b8',
              transition: 'all 0.15s',
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'db'        && <DBPage />}
      {tab === 'analysis'  && <AnalysisPage />}
      {tab === 'recommend' && <RecommendPage />}
      {tab === 'report'    && <ReportPage />}
    </div>
  )
}
