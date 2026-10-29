// Startup replies are diagnostic evidence; missing/expired evidence stays unknown.
export function servoReplyStatus(row) {
  if (!Object.hasOwn(row, 'responding')) return null;
  if (row.responding === true) return { word: '有应答', kind: 'ok' };
  if (row.responding === false) return { word: '未应答', kind: 'bad' };
  return { word: '未知', kind: '' };
}

export function startupStageCopy(st) {
  if (st?.posture !== 'starting' || !st.start_wait?.text) return null;
  return { h: st.start_wait.text,
    sub: `${st.starting_long ? `已经 ${st.starting_s} 秒了。` : ''}${st.start_error ? `原文：${st.start_error}。` : ''}去日志页看主程序最后说了什么。`,
    act: { href: '#/logs', label: '去日志页' } };
}
