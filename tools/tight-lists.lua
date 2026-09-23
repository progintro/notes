-- LaTeX \item bodies arrive as paragraphs, which makes every list "loose": a blank
-- line between each bullet in the Markdown and extra spacing on the page. The slides
-- were tight lists, so paragraphs directly inside list items become plain blocks.
local function tighten(items)
  for _, item in ipairs(items) do
    for i, blk in ipairs(item) do
      if blk.t == "Para" then item[i] = pandoc.Plain(blk.content) end
    end
  end
  return items
end

function BulletList(l) l.content = tighten(l.content); return l end
function OrderedList(l) l.content = tighten(l.content); return l end
