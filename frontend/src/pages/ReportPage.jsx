import { useQuery } from '@tanstack/react-query'
import { getReport } from '../api/lottery'

const ZONE_COLOR = { hot: '#f97316', neutral: '#3b82f6', cold: '#06b6d4' }

function Card({ children, style = {} }) {
  return (
    <div style={{ background: '#1e293b', borderRadius: 8, padding: '16px 20px', ...style }}>
      {children}
    </div>
  )
}

function SectionTitle({ children }) {
  return (
    <h2 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#64748b',
                 textTransform: 'uppercase', letterSpacing: '0.05em',
                 marginBottom: 12 }}>
      {children}
    </h2>
  )
}

function SegBar({ hot, neutral, cold }) {
  const total = hot + neutral + cold
  const pct = v => (v / total * 100).toFixed(1)
  return (
    <div>
      <div style={{ display: 'flex', height: 20, borderRadius: 6, overflow: 'hidden', marginBottom: 8 }}>
        <div style={{ width: `${pct(hot)}%`, background: ZONE_COLOR.hot }} />
        <div style={{ width: `${pct(neutral)}%`, background: ZONE_COLOR.neutral }} />
        <div style={{ width: `${pct(cold)}%`, background: ZONE_COLOR.cold }} />
      </div>
      <div style={{ display: 'flex', gap: 16, fontSize: '0.8rem' }}>
        {[['🔥 Hot', hot, 'hot'], ['〰 중립', neutral, 'neutral'], ['🧊 Cold', cold, 'cold']].map(([label, v, z]) => (
          <span key={z} style={{ color: ZONE_COLOR[z] }}>
            {label}: <strong>{v}개</strong> ({pct(v)}%)
          </span>
        ))}
      </div>
    </div>
  )
}

export default function ReportPage() {
  const { data: report, isLoading } = useQuery({
    queryKey: ['report'],
    queryFn: getReport,
  })

  if (isLoading) return <p style={{ color: '#94a3b8' }}>리포트 생성 중...</p>
  if (!report) return null

  const { quality, seg_dist, hist_comp, strategy_scores, top_cold, top_hot, personas } = report

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* 헤더 */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <Card style={{ flex: 1, borderLeft: `4px solid ${quality.color}` }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: 4 }}>현재 시장 상황</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: quality.color }}>
            {quality.icon} {quality.grade}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: 4 }}>{quality.desc}</div>
          <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: 2 }}>품질 점수: {quality.score}/50</div>
        </Card>
        <Card style={{ flex: 1 }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: 4 }}>다음 추첨</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{report.next_round}회</div>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: 4 }}>
            기준 회차: {report.last_round}회 ({report.last_draw_date})
          </div>
          <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: 2 }}>
            총 {report.total_draws}회차 데이터
          </div>
        </Card>
      </div>

      {/* 구간 분포 */}
      <Card>
        <SectionTitle>현재 번호 구간 분포</SectionTitle>
        <SegBar hot={seg_dist.hot} neutral={seg_dist.neutral} cold={seg_dist.cold} />
      </Card>

      {/* 역사적 당첨 구성 */}
      <Card>
        <SectionTitle>최근 30회 당첨번호 구성</SectionTitle>
        <div style={{ display: 'flex', gap: 16, fontSize: '0.85rem' }}>
          {[['🔥 Hot', hist_comp.hot, 'hot'], ['〰 중립', hist_comp.neutral, 'neutral'], ['🧊 Cold', hist_comp.cold, 'cold']].map(([label, v, z]) => (
            <div key={z} style={{ flex: 1, textAlign: 'center', padding: '10px 0',
                                   borderRadius: 6, background: '#0f172a' }}>
              <div style={{ color: ZONE_COLOR[z], fontWeight: 700, fontSize: '1.1rem' }}>{v}%</div>
              <div style={{ color: '#64748b', fontSize: '0.75rem', marginTop: 2 }}>{label}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* 전략 점수 */}
      <Card>
        <SectionTitle>전략별 적합도 점수</SectionTitle>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
            <thead>
              <tr style={{ color: '#64748b', borderBottom: '1px solid #334155' }}>
                {['전략', '종합', '커버리지', '구성 적합', '상황 적합', '판정'].map(h => (
                  <th key={h} style={{ padding: '7px 10px', textAlign: 'center' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {strategy_scores.map((s, i) => (
                <tr key={s.key} style={{ borderBottom: '1px solid #1e293b',
                                          background: i === 0 ? '#1a2744' : 'transparent' }}>
                  <td style={{ padding: '8px 10px', fontWeight: 600 }}>{s.label}</td>
                  <td style={{ padding: '8px 10px', textAlign: 'center', fontWeight: 700,
                                color: s.rank_color }}>{s.total}</td>
                  <td style={{ padding: '8px 10px', textAlign: 'center' }}>{s.coverage}%</td>
                  <td style={{ padding: '8px 10px', textAlign: 'center' }}>{s.comp_fit}</td>
                  <td style={{ padding: '8px 10px', textAlign: 'center' }}>{s.situ_fit}</td>
                  <td style={{ padding: '8px 10px', textAlign: 'center' }}>
                    <span style={{ color: s.rank_color, fontWeight: 600 }}>{s.rank_label}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* 주목 번호 */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <Card style={{ flex: 1, minWidth: 200 }}>
          <SectionTitle>🧊 주목 Cold 번호</SectionTitle>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {top_cold.map(n => (
              <div key={n.number} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                                width: 30, height: 30, borderRadius: '50%', background: ZONE_COLOR.cold,
                                color: '#fff', fontWeight: 700, fontSize: '0.82rem', flexShrink: 0 }}>
                  {n.number}
                </span>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  {n.streak}회 미출현 · 점수 {n.score}
                </span>
              </div>
            ))}
          </div>
        </Card>
        <Card style={{ flex: 1, minWidth: 200 }}>
          <SectionTitle>🔥 주목 Hot 번호</SectionTitle>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {top_hot.length === 0
              ? <p style={{ color: '#475569', fontSize: '0.82rem' }}>해당 번호 없음</p>
              : top_hot.map(n => (
                <div key={n.number} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                                  width: 30, height: 30, borderRadius: '50%', background: ZONE_COLOR.hot,
                                  color: '#fff', fontWeight: 700, fontSize: '0.82rem', flexShrink: 0 }}>
                    {n.number}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                    최근10회 {n.recent_10}번 · 점수 {n.score}
                  </span>
                </div>
              ))
            }
          </div>
        </Card>
      </div>

      {/* 성향별 추천 */}
      <Card>
        <SectionTitle>성향별 추천 전략</SectionTitle>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
          {personas.map(p => (
            <div key={p.title} style={{ background: '#0f172a', borderRadius: 6, padding: '12px 14px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: 4 }}>
                {p.icon} {p.title}
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#60a5fa', marginBottom: 4 }}>
                {p.label}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{p.reason}</div>
              <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: 4 }}>
                종합 점수: {p.total}
              </div>
            </div>
          ))}
        </div>
      </Card>

    </div>
  )
}
