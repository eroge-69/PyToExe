��i m p o r t   o s 
 i m p o r t   s u b p r o c e s s 
 i m p o r t   s y s 
 i m p o r t   t i m e 
 
 #   1 .   V e r z e i c h n i s s e   e r s t e l l e n 
 b a s e _ p a t h   =   r " C : \ G o l i a t h _ A I \ p h a s e 1 " 
 s u b d i r s   =   [ " o u t p u t " ,   " l o g s " ,   " r s s " ,   " f e e d s " ] 
 f o r   s u b   i n   s u b d i r s : 
         p a t h   =   o s . p a t h . j o i n ( b a s e _ p a t h ,   s u b ) 
         o s . m a k e d i r s ( p a t h ,   e x i s t _ o k = T r u e ) 
 
 p r i n t ( " [ S E T U P ]   V e r z e i c h n i s s e   e r s t e l l t . " ) 
 
 #   2 .   P f a d e   d e f i n i e r e n 
 p r i m u s _ p a t h   =   o s . p a t h . j o i n ( b a s e _ p a t h ,   " p r i m u s . p y " ) 
 t a s k _ n a m e   =   " G o l i a t h A I _ P r i m u s _ H o u r l y " 
 
 #   3 .   T a s k   S c h e d u l e r - B e f e h l   v o r b e r e i t e n 
 s c h t a s k _ c m d   =   [ 
         " s c h t a s k s " , 
         " / C r e a t e " , 
         " / F " , 
         " / S C " ,   " H O U R L Y " , 
         " / T N " ,   t a s k _ n a m e , 
         " / T R " ,   f ' " { s y s . e x e c u t a b l e } "   " { p r i m u s _ p a t h } " ' , 
         " / S T " ,   " 0 0 : 0 0 " 
 ] 
 
 #   4 .   T a s k   e r s t e l l e n   ( A d m i n i s t r a t o r r e c h t e   n � t i g ) 
 t r y : 
         s u b p r o c e s s . r u n ( s c h t a s k _ c m d ,   c h e c k = T r u e ) 
         p r i n t ( f " [ S E T U P ]   T a s k   ' { t a s k _ n a m e } '   i m   T a s k p l a n e r   r e g i s t r i e r t . " ) 
 e x c e p t   s u b p r o c e s s . C a l l e d P r o c e s s E r r o r   a s   e : 
         p r i n t ( f " [ F E H L E R ]   K o n n t e   T a s k   n i c h t   e r s t e l l e n :   { e } " ) 
 
 #   5 .   P r i m u s   j e t z t   s o f o r t   s t a r t e n 
 i f   o s . p a t h . e x i s t s ( p r i m u s _ p a t h ) : 
         p r i n t ( " [ S T A R T ]   S t a r t e   P r i m u s   e i n m a l i g . . . " ) 
         s u b p r o c e s s . P o p e n ( [ s y s . e x e c u t a b l e ,   p r i m u s _ p a t h ] ) 
         p r i n t ( " [ S T A R T ]   P r i m u s   g e s t a r t e t . " ) 
 e l s e : 
         p r i n t ( " [ F E H L E R ]   p r i m u s . p y   w u r d e   n i c h t   g e f u n d e n .   S t e l l e   s i c h e r ,   d a s s   e s   u n t e r   C : \ \ G o l i a t h _ A I \ \ p h a s e 1   l i e g t . " ) 
 
 #   6 .   K u r z   w a r t e n   u n d   A b s c h l u s s m e l d u n g 
 t i m e . s l e e p ( 2 ) 
 p r i n t ( " \ n '  E i n r i c h t u n g   a b g e s c h l o s s e n .   G o l i a t h   i s t   b e r e i t . " ) 
 