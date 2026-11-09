"""Conditional file, companion-route, and dropped-weapon eligibility."""
from pathlib import Path
import subprocess,tempfile
h=(Path(__file__).resolve().parents[1]/'src'/'item_state.h').read_text()
with tempfile.TemporaryDirectory() as d:
 p=Path(d);c=p/'test.c';out=p/'test'
 c.write_text('''#include <assert.h>
'''+h+'''
#define SET(b,n) ((b)[(n)/32]|=1u<<((n)%32))
int main(void){
 unsigned b0[8]={0},b1[16]={0},b3[16]={0};
 /* Both characters, all 16 mask combinations; unrelated ammo is unaffected. */
 for(int j=0;j<2;j++)for(unsigned masks=0;masks<16;masks++){
  for(int i=0;i<16;i++)b1[i]=0;
  for(unsigned n=0;n<4;n++)if(masks&(1u<<n))SET(b1,50+n);
  assert(placed_item_available(7,463,11,j,b0,b1,b3)==(masks==15));
  assert(placed_item_available(7,86,64,j,b0,b1,b3));
 }
 /* Serum: native 0x4a0bb8.. spawns one of two slots, never both, and none before the poison event. */
 for(int i=0;i<16;i++)b1[i]=0;
 assert(!placed_item_available(4,128,0,0,b0,b1,b3)&&!placed_item_available(4,129,0,0,b0,b1,b3));
 SET(b0,97);assert(placed_item_available(4,128,0,0,b0,b1,b3)&&!placed_item_available(4,129,0,0,b0,b1,b3));
 for(int i=0;i<8;i++)b0[i]=0;
 SET(b1,41);assert(!placed_item_available(4,128,0,0,b0,b1,b3)&&placed_item_available(4,129,0,0,b0,b1,b3));
 for(int i=0;i<16;i++)b1[i]=0;
 /* Garden Shed second set waits for the Helmet Key; the first set does not. */
 for(int j=0;j<2;j++){assert(!placed_item_available(7,119,27,j,b0,b1,b3));assert(placed_item_available(7,80,27,j,b0,b1,b3));}
 SET(b3,69);for(int j=0;j<2;j++)assert(placed_item_available(7,119,27,j,b0,b1,b3));
 for(int i=0;i<16;i++)b3[i]=0;
 for(int i=0;i<16;i++)b1[i]=0;
 /* Before either room has selected a location, neither candidate should be advertised. */
 assert(!placed_item_available(5,509,0,1,b0,b1,b3));assert(!placed_item_available(5,509,24,1,b0,b1,b3));
 SET(b1,91);assert(placed_item_available(5,509,0,1,b0,b1,b3));assert(!placed_item_available(5,509,24,1,b0,b1,b3));
 b1[91/32]=0;SET(b1,269);assert(!placed_item_available(5,509,0,0,b0,b1,b3));assert(placed_item_available(5,509,24,0,b0,b1,b3));
 for(int jill=0;jill<=1;jill++){
  for(int dead=0;dead<=1;dead++)for(int ready=0;ready<=1;ready++){
   for(int i=0;i<8;i++)b0[i]=0;for(int i=0;i<16;i++)b1[i]=0;
   if(dead)SET(b0,jill?37:34);if(ready)SET(b1,216);
   assert(placed_item_available(4,405,148,jill,b0,b1,b3)==(dead&&ready));
   assert(placed_item_available(1,45,129,jill,b0,b1,b3)==dead);
   assert(placed_item_available(1,47,140,jill,b0,b1,b3)==dead);
  }
 }
 for(int i=0;i<8;i++)b0[i]=0;
 assert(!placed_item_available(4,23,53,1,b0,b1,b3));SET(b0,7);
 assert(placed_item_available(4,23,53,1,b0,b1,b3));assert(!placed_item_available(4,23,53,0,b0,b1,b3));
 assert(!placed_item_available(4,401,122,0,b0,b1,b3));SET(b0,98);
 assert(placed_item_available(4,401,122,0,b0,b1,b3));assert(!placed_item_available(4,401,122,1,b0,b1,b3));
 assert(!placed_item_available(4,123,93,1,b0,b1,b3));SET(b0,37);
 assert(placed_item_available(4,123,93,1,b0,b1,b3));assert(!placed_item_available(4,123,93,0,b0,b1,b3));
 assert(placed_item_available(4,388,97,1,b0,b1,b3)); /* Jewelry Box3 not an inventory-derived reward. */
}
''')
 subprocess.run(['clang',str(c),'-o',str(out)],check=True);subprocess.run([str(out)],check=True)
print('PASS: conditional pickup, crypt masks, companion and weapon state truth tables')
