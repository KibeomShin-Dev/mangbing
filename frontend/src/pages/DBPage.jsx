import { useQuery } from '@tanstack/react-query'
import { getDBStatus, getRecentDraws } from '../api/lottery'

function Ball({ number }) {
  const color =
    number <= 10 ? '#eab308' :
    number <= 20 ? '#3b82f6' :
    number <= 30 ? '#ef4444' :
    number <= 40 ? '#a855f7' : '#10b981'

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      width: 32, height: 32, borderRadius: '50%',
      background: color, color: '#fff',
      fontWeight: 700, fontSize: '0.8rem', marginRight: 4,
    }}>
      {number}
    </span>
  )
}

export default function DBPage() {
  const { data: status, isLoading: loadingStatus } = useQuery({
    queryKey: ['db-status'],
    queryFn: getDBStatus,
  })
  const { data: draws, isLoading: loadingDraws } = useQuery({
    queryKey: ['recent-draws'],
    queryFn: () => getRecentDraws(20),
  })

  if (loadingStatus || loadingDraws) return <p style={{ color: '#94a3b8' }}>로딩 중...</p>

  return (
    <div>
      {status && (
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: 12, marginBottom: 28,
        }}>
          {[
            ['총 회차', `${status.total_rounds}회`],
            ['최신 회차', `${status.last_round}회`],
            ['최신 추첨일', status.last_draw_date],
            ['첫 회차', `${status.first_round}회`],
          ].map(([label, value]) => (
            <div key={label} style={{
              background: '#1e293b', borderRadius: 8, padding: '14px 18px',
            }}>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: 4 }}>{label}</div>
              <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>{value}</div>
            </div>
          ))}
        </div>
      )}

      <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12, color: '#94a3b8' }}>
        최근 20회차
      </h2>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ color: '#64748b', borderBottom: '1px solid #334155' }}>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>회차</th>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>추첨일</th>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>당첨번호</th>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>보너스</th>
            </tr>
          </thead>
          <tbody>
            {draws && [...draws].reverse().map(d => (
              <tr key={d.round_no} style={{ borderBottom: '1px solid #1e293b' }}>
                <td style={{ padding: '8px 12px', fontWeight: 600 }}>{d.round_no}</td>
                <td style={{ padding: '8px 12px', color: '#94a3b8' }}>{d.draw_date}</td>
                <td style={{ padding: '8px 12px' }}>
                  {d.numbers.map(n => <Ball key={n} number={n} />)}
                </td>
                <td style={{ padding: '8px 12px' }}>
                  <Ball number={d.bonus} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
