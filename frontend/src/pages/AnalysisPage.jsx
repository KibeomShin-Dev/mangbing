import { useQuery } from '@tanstack/react-query'
import { getNumberStats } from '../api/lottery'

const ZONE_COLOR = { hot: '#f97316', neutral: '#3b82f6', cold: '#06b6d4' }
const ZONE_LABEL = { hot: '🔥 Hot', neutral: '〰 중립', cold: '🧊 Cold' }

export default function AnalysisPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['number-stats'],
    queryFn: getNumberStats,
  })

  if (isLoading) return <p style={{ color: '#94a3b8' }}>분석 중...</p>
  if (!stats) return null

  const sorted = [...stats].sort((a, b) => b.score - a.score)

  const zoneCounts = stats.reduce((acc, s) => {
    acc[s.zone] = (acc[s.zone] || 0) + 1
    return acc
  }, {})

  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        {['hot', 'neutral', 'cold'].map(zone => (
          <div key={zone} style={{
            flex: 1, background: '#1e293b', borderRadius: 8, padding: '12px 16px',
            borderLeft: `4px solid ${ZONE_COLOR[zone]}`,
          }}>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{ZONE_LABEL[zone]}</div>
            <div style={{ fontWeight: 700, fontSize: '1.4rem', color: ZONE_COLOR[zone] }}>
              {zoneCounts[zone] ?? 0}개
            </div>
            <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: 2 }}>
              {zone === 'hot' ? '0~5회 미출현' : zone === 'neutral' ? '6~9회 미출현' : '10회+ 미출현'}
            </div>
          </div>
        ))}
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
          <thead>
            <tr style={{ color: '#64748b', borderBottom: '1px solid #334155' }}>
              {['번호', '구간', '점수', '연속미출', '최근10', '최근30', '최근100', '전체'].map(h => (
                <th key={h} style={{ padding: '8px 10px', textAlign: 'center' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map(s => (
              <tr key={s.number} style={{ borderBottom: '1px solid #1e293b' }}>
                <td style={{ padding: '7px 10px', textAlign: 'center', fontWeight: 700 }}>
                  <span style={{
                    display: 'inline-block', width: 28, height: 28, lineHeight: '28px',
                    borderRadius: '50%', background: ZONE_COLOR[s.zone], color: '#fff',
                    fontSize: '0.8rem',
                  }}>{s.number}</span>
                </td>
                <td style={{ padding: '7px 10px', textAlign: 'center', color: ZONE_COLOR[s.zone], fontWeight: 600 }}>
                  {ZONE_LABEL[s.zone]}
                </td>
                <td style={{ padding: '7px 10px', textAlign: 'center', fontWeight: 700 }}>{s.score}</td>
                <td style={{ padding: '7px 10px', textAlign: 'center' }}>{s.cold_streak}</td>
                <td style={{ padding: '7px 10px', textAlign: 'center' }}>{s.recent_10_count}</td>
                <td style={{ padding: '7px 10px', textAlign: 'center' }}>{s.recent_30_count}</td>
                <td style={{ padding: '7px 10px', textAlign: 'center' }}>{s.recent_100_count}</td>
                <td style={{ padding: '7px 10px', textAlign: 'center', color: '#64748b' }}>{s.total_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
