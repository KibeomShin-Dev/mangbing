import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { getRecommendations } from '../api/lottery'

const STRATEGIES = [
  { id: 'balanced',      label: '균형형',     desc: 'Hot 2 + 중립 2 + Cold 2' },
  { id: 'hotfocus',      label: 'Hot 집중',   desc: 'Hot 3 + 중립 2 + Cold 1' },
  { id: 'neutralfocus',  label: '중립 집중',   desc: 'Hot 1 + 중립 3 + Cold 2' },
  { id: 'coldfocus',     label: 'Cold 집중',  desc: 'Hot 1 + 중립 1 + Cold 4' },
  { id: 'experimental',  label: '실험적',     desc: 'Hot 2 + 중립 1 + Cold 3' },
]

const ZONE_COLOR = { hot: '#f97316', neutral: '#3b82f6', cold: '#06b6d4' }

function Ball({ number, zone }) {
  const color = zone ? ZONE_COLOR[zone] : '#475569'
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      width: 36, height: 36, borderRadius: '50%',
      background: color, color: '#fff',
      fontWeight: 700, fontSize: '0.9rem', marginRight: 6,
    }}>
      {number}
    </span>
  )
}

export default function RecommendPage() {
  const [strategy, setStrategy] = useState('balanced')
  const [count, setCount] = useState(5)

  const { mutate, data: results, isPending } = useMutation({
    mutationFn: () => getRecommendations(strategy, count),
  })

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
        {STRATEGIES.map(s => (
          <button
            key={s.id}
            onClick={() => setStrategy(s.id)}
            style={{
              padding: '8px 14px', borderRadius: 6, border: 'none', cursor: 'pointer',
              background: strategy === s.id ? '#3b82f6' : '#1e293b',
              color: strategy === s.id ? '#fff' : '#94a3b8',
              fontWeight: 600, fontSize: '0.85rem',
            }}
          >
            {s.label}
            <span style={{ fontSize: '0.72rem', display: 'block', fontWeight: 400, color: strategy === s.id ? '#bfdbfe' : '#475569' }}>
              {s.desc}
            </span>
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <label style={{ color: '#94a3b8', fontSize: '0.875rem' }}>조합 수:</label>
        {[1, 3, 5, 10].map(n => (
          <button
            key={n}
            onClick={() => setCount(n)}
            style={{
              padding: '5px 14px', borderRadius: 6, border: 'none', cursor: 'pointer',
              background: count === n ? '#1d4ed8' : '#1e293b',
              color: count === n ? '#fff' : '#94a3b8',
              fontWeight: 600,
            }}
          >
            {n}
          </button>
        ))}
        <button
          onClick={() => mutate()}
          disabled={isPending}
          style={{
            marginLeft: 8, padding: '8px 24px', borderRadius: 6, border: 'none', cursor: 'pointer',
            background: '#22c55e', color: '#fff', fontWeight: 700, fontSize: '0.95rem',
          }}
        >
          {isPending ? '생성 중...' : '번호 추천'}
        </button>
      </div>

      {results && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {results.map((r, i) => (
            <div key={i} style={{
              background: '#1e293b', borderRadius: 8, padding: '14px 18px',
              display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap',
            }}>
              <span style={{ color: '#64748b', fontWeight: 600, minWidth: 24 }}>#{i + 1}</span>
              <div>
                {r.numbers.map(n => <Ball key={n} number={n} />)}
              </div>
              <div style={{ marginLeft: 'auto', display: 'flex', gap: 10, fontSize: '0.8rem' }}>
                <span style={{ color: ZONE_COLOR.hot }}>🔥 {r.hot_count}</span>
                <span style={{ color: ZONE_COLOR.neutral }}>〰 {r.neutral_count}</span>
                <span style={{ color: ZONE_COLOR.cold }}>🧊 {r.cold_count}</span>
                <span style={{ color: '#64748b' }}>균형 {r.balance_score}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
