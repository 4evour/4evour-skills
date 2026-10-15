-- 保留原文；只在渲染 AST 中标注组件、合并重复标题并分离摘要区。
local enabled, title = false, ''
local function quote(value) return '"' .. tostring(value or ''):gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n') .. '"' end
local function render_blocks(blocks) return pandoc.write(pandoc.Pandoc(blocks), 'typst') end
local function configure(meta)
  enabled = meta['design-layout'] ~= nil
  title = pandoc.utils.stringify(meta.title or '')
end
local function component(el)
  if not enabled or not FORMAT:match('typst') then return end
  if el.classes:includes('kami-metrics') or el.classes:includes('kami-columns') then
    local cells = {}
    for _, block in ipairs(el.content) do table.insert(cells, '[' .. render_blocks({block}) .. ']') end
    local count = el.classes:includes('kami-metrics') and math.min(3, #cells) or 2
    if #cells == 0 then return {} end
    return pandoc.RawBlock('typst', '#kami-tiles(columns: ' .. count .. ', ' .. table.concat(cells, ', ') .. ')')
  end
  if el.classes:includes('kami-divider') then
    local text = pandoc.utils.stringify(el.content)
    return pandoc.RawBlock('typst', '#kami-separator(label: ' .. (text == '' and 'none' or quote(text)) .. ')')
  end
  if el.classes:includes('kami-tags') then
    local items = {}
    for text in pandoc.utils.stringify(el.content):gmatch('[^|]+') do
      text = text:match('^%s*(.-)%s*$')
      if text ~= '' then table.insert(items, '[' .. render_blocks({pandoc.Plain({pandoc.Str(text)})}) .. ']') end
    end
    return pandoc.RawBlock('typst', '#kami-chips(' .. table.concat(items, ', ') .. ')')
  end
  for _,kind in ipairs({'lead','takeaway','note','pullquote','metric','info','alert','success','step'}) do
    if el.classes:includes('kami-' .. kind) then
      local opening = '#kami-panel(kind: ' .. quote(kind) .. ', title: ' .. (el.attributes.title and '[' .. pandoc.write(pandoc.Pandoc({pandoc.Plain({pandoc.Str(el.attributes.title)})}), 'typst') .. ']' or 'none') .. ', label: ' .. (el.attributes.label and quote(el.attributes.label) or 'none') .. ', value: ' .. (el.attributes.value and quote(el.attributes.value) or 'none') .. ')['
      return pandoc.RawBlock('typst', opening .. render_blocks(el.content) .. ']')
    end
  end
end
local function arrange(doc)
  if not enabled or not FORMAT:match('typst') then return end
  local front, main, in_main, duplicate_removed = {}, {}, false, false
  for _,block in ipairs(doc.blocks) do
    if block.t == 'Header' and block.level == 1 and not duplicate_removed and pandoc.utils.stringify(block.content) == title then
      duplicate_removed = true
    else
      if block.t == 'Header' then in_main = true end
      table.insert(in_main and main or front, block)
    end
  end
  if #main == 0 then main, front = front, {} end
  local min_level = 6
  for _,block in ipairs(main) do if block.t == 'Header' then min_level = math.min(min_level, block.level) end end
  if min_level ~= 6 and min_level ~= 2 then
    for _,block in ipairs(main) do if block.t == 'Header' then block.level = math.min(6, block.level + 2 - min_level) end end
  end
  local function build_flow(opening, blocks, continuation)
    local chunks, pending = {}, {}
    for _,block in ipairs(blocks) do
      table.insert(pending, block)
      if block.t ~= 'Header' then table.insert(chunks, '[' .. render_blocks(pending) .. ']'); pending = {} end
    end
    if #pending > 0 then table.insert(chunks, '[' .. render_blocks(pending) .. ']') end
    local chunk_text = #chunks == 0 and '()' or '(' .. table.concat(chunks, ', ') .. ',)'
    return '#kami-flow(continuation: ' .. tostring(continuation) .. ', front: [' .. render_blocks(opening) .. '], main: [' .. render_blocks(blocks) .. '], chunks: ' .. chunk_text .. ')'
  end
  local results, section, continuation = {}, {}, false
  for _,block in ipairs(main) do
    if block.t == 'RawBlock' and block.format == 'typst' and block.text:match('^%s*#pagebreak%(%)%s*$') then
      table.insert(results, pandoc.RawBlock('typst', build_flow(front, section, continuation)))
      table.insert(results, block)
      front, section, continuation = {}, {}, true
    else table.insert(section, block) end
  end
  table.insert(results, pandoc.RawBlock('typst', build_flow(front, section, continuation)))
  return pandoc.Pandoc(results, doc.meta)
end
return {{Meta=configure}, {Div=component}, {Pandoc=arrange}}
