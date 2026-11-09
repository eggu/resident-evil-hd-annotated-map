"""Compile actual marker guard; check insertion/completion/pickup combinations."""
from pathlib import Path
import re,subprocess,tempfile
p=Path(__file__).resolve().parents[1]/'src'
s=(p/'re1_mapnames.c').read_text()
guard=re.search(r'if \(l->kind == 4 && l->flag == 344 && .*?\) continue;',s).group()
with tempfile.TemporaryDirectory() as d:
 c=Path(d)/'check.c';exe=Path(d)/'check'
 c.write_text('''#include <assert.h>
typedef unsigned U32;
static int bitn(const U32 *b,U32 i,U32 n){return i<n && (b[i/32]>>(i%32)&1);}
struct Label {int kind; unsigned flag;};
int main(void){
 for(unsigned inserted=0;inserted<2;inserted++)
 for(unsigned done=0;done<2;done++)
 for(unsigned taken=0;taken<2;taken++){
  U32 b1[16]={0},b3[16]={0}; b1[5]=inserted; b1[4]=done<<30;
  if(taken)b3[344/32]|=1u<<(344%32);
  struct Label rows[]={{4,344}};
  int visible=0;
  for(int i=0;i<1;i++){struct Label *l=rows+i;
   if(bitn(b3,l->flag,512))continue;
''' + guard + '''
   visible++;
  }
  assert(visible==(inserted&&!done&&!taken));
 }
}
''')
 subprocess.run(['clang',str(c),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
print('PASS:8 insertion/completion/pickup states; completed generator hides Cylinder Shaft')
