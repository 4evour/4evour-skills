-- 仅转换显式侧栏和 Tufte 的旁注，原始文章另行完整保留。
local use_tufte = false
local note_count = 0
local function configure(meta)
  use_tufte = meta['studio-tufte'] == true
  note_count = 0
end
local function sidenote(el)
  if FORMAT:match('typst') and use_tufte then
    note_count = note_count + 1
    local body = pandoc.write(pandoc.Pandoc(el.content), 'typst')
    local number = tostring(note_count)
    return pandoc.RawInline('typst', '#super[' .. number .. ']#note(dy: 0pt, numbered: false)[#super[' .. number .. '] ' .. body .. ']')
  end
end
local function sidebar(el)
  if FORMAT:match('typst') and el.classes:includes('sidebar') then
    table.insert(el.content, 1, pandoc.RawBlock('typst', '#studio-sidebar['))
    table.insert(el.content, pandoc.RawBlock('typst', ']'))
    return el.content
  end
end
return {{Meta = configure}, {Note = sidenote}, {Div = sidebar}}
