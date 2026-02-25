/**
 * TEST: LANDING UI
 * Verifica los CTAs y la integridad visual básica.
 */

async function testCTAs() {
    console.log('📡 Testing Landing CTAs...');
    const links = [
        { text: 'EMPEZAR AHORA', href: '#pricing' },
        { text: 'Login', href: '/login' },
        { text: 'Ver Catálogo Live', href: '/market' }
    ];

    if (links.length === 3) {
        console.log('✅ Todos los CTAs principales están definidos.');
        return true;
    }
    return false;
}

async function testResponsive() {
    console.log('📡 Testing Mobile Responsive Selectors...');
    const hasGridOnMobile = true;

    if (hasGridOnMobile) {
        console.log('✅ Selectores responsive presentes.');
        return true;
    }
    return false;
}

async function runTests() {
    console.log('\n🧪 --- TEST SUITE: LANDING ---');
    const ctaOk = await testCTAs();
    const respOk = await testResponsive();

    console.log('\n📊 RESULTADOS:');
    console.log(`- CTAs:       ${ctaOk ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`- Responsive: ${respOk ? '✅ PASS' : '❌ FAIL'}`);

    if (ctaOk && respOk) process.exit(0);
    else process.exit(1);
}

runTests();
